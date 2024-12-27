import hashlib
from datetime import datetime, timedelta
import random
from flask import render_template, request, url_for,session, redirect
from app import dao, utils, login, app, db, mail
from flask_login import login_user, login_required, logout_user, current_user
from app.models import Role, TeacherInfo, StaffInfo, AdminInfo, StudentInfo
from flask_mail import Mail, Message


@app.route("/")
def index():
    return render_template('index.html')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/login", methods=['GET', 'POST'])
def login_process():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            session['login_error'] = 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.'
            return render_template('login.html')

        user = dao.check_user(username, password)
        if user:
            login_user(user=user)
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role.name

            user_role = dao.get_user_role(user.role)

            if user_role in ("admin", "staff"):
                return redirect(url_for("admin.index"))

            if 'login_error' in session:
                session.pop('login_error')

            return redirect('/')
        else:
            session['login_error'] = 'Tên đăng nhập hoặc mật khẩu không đúng.'

    login_error = session.pop('login_error', None)

    return render_template('login.html', login_error=login_error)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html',
                           username=current_user.username,
                           role=current_user.role.name)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()

    return redirect(url_for('login_process'))


@app.route("/transcripts", methods=['get', 'post'])
@login_required
def transcript_process():
    filters = None
    transcript_data = None
    if current_user.role == Role.TEACHER:
        teacher_info = dao.get_teacher(current_user.id)
        school_year = dao.get_current_school_year()
        semesters = [
            "FIRST_TERM",
            "SECOND_TERM"
        ]
        subjects = dao.get_subject_names_by_teacher(school_year_id=school_year.id, teacher_info_id=teacher_info.id)
        transcript_data = None
        if request.method == 'POST':
            if request.form.get('action') == 'filter':
                selected_semester = request.form.get('semester')
                selected_subject = request.form.get('subject')
                transcripts = dao.get_transcripts(teacher_info_id=teacher_info.id, school_year_id=school_year.id,
                                                  semester_type=selected_semester, subject_name=selected_subject)
                transcript_data = []
                for transcript in transcripts:
                    transcript_data.append({
                        'school_year': transcript.school_year_name,
                        'semester_type': transcript.semester_type.name,
                        'classroom_name': transcript.classroom_name,
                        'subject_name': transcript.subject_name,
                        'transcript_id': transcript.id
                    })
        filters = [
            {"label": "Semester", "id": "semester", "data": semesters},
            {"label": "Subject", "id": "subject", "data": subjects},
        ]

    return render_template('transcript.html', filters=filters, transcript_data=transcript_data)


@app.route('/transcripts/<int:transcript_id>', methods=['GET', 'POST'])
@login_required
def score_process(transcript_id):
    if current_user.role == Role.TEACHER:
        transcript_info = dao.get_transcripts(transcript_id=transcript_id)
        transcript = dao.get_students_and_scores_by_transcript_id(transcript_id)

        if request.method == 'POST':
            # Lấy dữ liệu từ form
            form_data = request.form
            updated_scores = []
            new_scores = []
            deleted_scores = []

            for key, value in form_data.items():
                value = value.strip()
                student_id, score_id, score_type, index = key.split('-')
                student_id = int(student_id)
                score_number = float(value) if value else None

                if score_id == 'new':
                    if score_number is not None:
                        new_scores.append({
                            'student_id': student_id,
                            'score_number': score_number,
                            'score_type': score_type,
                            'transcript_id': transcript_id
                        })
                else:
                    score_id = int(score_id)
                    for student in transcript:
                        if student['student_id'] == student_id:
                            original_scores = student[score_type]
                            original_score = next((s for s in original_scores if s['score_id'] == score_id), None)

                            if original_score:
                                if score_number is None:
                                    deleted_scores.append(score_id)
                                elif original_score['score'] != score_number:
                                    updated_scores.append({
                                        'score_id': score_id,
                                        'score_number': score_number
                                    })
                            break

            for score in new_scores:
                dao.create_score(
                    score_value=score['score_number'],
                    student_info_id=score['student_id'],
                    transcript_id=score['transcript_id'],
                    score_type=score['score_type'],

                )
            for score in updated_scores:
                dao.update_score(
                    score_id=score['score_id'],
                    new_value=score['score_number']
                )
            for score_id in deleted_scores:
                dao.delete_score(score_id)

            return redirect(url_for('score_process', transcript_id=transcript_id))

        return render_template(
            'score.html',
            transcript=transcript,
            transcript_info=transcript_info,
            transcript_id=transcript_id
        )

@app.route('/transcripts/<int:transcript_id>/export', methods=['GET', 'POST'])
@login_required
def export_transcript(transcript_id):
    if current_user.role == Role.TEACHER:
        transcript_data = dao.get_transcript_avg(transcript_id)

        return render_template('export_transcript.html', transcript=transcript_data)


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.context_processor
def common_response():
    return {
        'Role': Role,
    }

@app.route("/send-otp", methods=["GET", "POST"])
@login_required
def send_otp():
    if request.method == "GET":
        return render_template("send-otp.html")  # Hiển thị trang gửi/nhập OTP

    # Phân biệt hành động (Gửi OTP hoặc Xác minh OTP)
    action = request.form.get("action")

    if action == "send":
        # Tạo và gửi OTP
        otp_code = str(random.randint(100000, 999999))  # Tạo OTP ngẫu nhiên
        expiration_time = datetime.now() + timedelta(minutes=5)  # Hết hạn sau 5 phút
        expiration_time_str = expiration_time.strftime('%Y-%m-%d %H:%M:%S')

        # Lưu OTP vào session
        session['otp'] = otp_code
        session['otp_expiration'] = expiration_time_str

        user = current_user
        email = None

        # Lấy email dựa trên vai trò người dùng
        if user.role == Role.TEACHER:
            teacher_info = TeacherInfo.query.filter_by(user_id=user.id).first()
            if teacher_info and teacher_info.email:
                email = teacher_info.email
        elif user.role == Role.STAFF:
            staff_info = StaffInfo.query.filter_by(user_id=user.id).first()
            if staff_info and staff_info.email:
                email = staff_info.email
        elif user.role == Role.ADMIN:
            admin_info = AdminInfo.query.filter_by(user_id=user.id).first()
            if admin_info and admin_info.email:
                email = admin_info.email
        elif user.role == Role.STUDENT:
            student_info = StudentInfo.query.filter_by(user_id=user.id).first()
            if student_info and student_info.email:
                email = student_info.email

        if not email:
            return render_template("send-otp.html", error="Không tìm thấy email liên kết với người dùng này.")

        # Gửi OTP qua email
        try:
            subject = "Mã OTP của bạn"
            body = f"Mã OTP của bạn là: {otp_code}\nMã sẽ hết hạn vào {expiration_time_str}."
            msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = body
            mail.send(msg)
            return render_template("send-otp.html", message="Mã OTP đã được gửi đến email của bạn.")
        except Exception as e:
            print(f"Lỗi khi gửi OTP: {e}")
            return render_template("send-otp.html", error="Không thể gửi mã OTP. Vui lòng thử lại sau.")

    elif action == "verify":
        # Xác minh OTP
        otp_input = request.form.get("otp")  # Lấy OTP từ form
        otp_code = session.get("otp")
        otp_expiration = session.get("otp_expiration")

        # Kiểm tra lỗi
        if not otp_code or not otp_expiration:
            error_message = "Không tìm thấy mã OTP. Vui lòng thử lại."
            return render_template("send-otp.html", error=error_message)

        if otp_input != otp_code:
            error_message = "Mã OTP không chính xác."
            return render_template("send-otp.html", error=error_message)

        if datetime.now() > datetime.strptime(otp_expiration, "%Y-%m-%d %H:%M:%S"):
            error_message = "Mã OTP đã hết hạn."
            return render_template("send-otp.html", error=error_message)

        if otp_input == otp_code and datetime.now() <= datetime.strptime(otp_expiration, "%Y-%m-%d %H:%M:%S"):
            # OTP hợp lệ, đánh dấu xác thực thành công
            session['otp_verified'] = True
            # Xóa OTP khỏi session
            session.pop("otp", None)
            session.pop("otp_expiration", None)
            return redirect(url_for("change_password"))
        else:
            return render_template("send-otp.html", error="Mã OTP không chính xác hoặc đã hết hạn.")

    # Nếu không phải hành động hợp lệ, trả về lỗi
    return render_template("send-otp.html", error="Hành động không được hỗ trợ.")



# Route để xác thực OTP và đổi mật khẩu
@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    # Kiểm tra xem OTP đã được xác thực chưa
    if not session.get('otp_verified'):
        # Nếu chưa xác thực OTP, chuyển hướng về trang gửi OTP
        return redirect(url_for("send_otp"))

    if request.method == "GET":
        return render_template("change_password.html")

    # Xử lý POST request
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if not new_password or not confirm_password:
        return render_template("change_password.html", error="Vui lòng nhập đầy đủ thông tin.")

    if new_password != confirm_password:
        return render_template("change_password.html", error="Mật khẩu không khớp. Vui lòng thử lại.")

    # Cập nhật mật khẩu trong cơ sở dữ liệu
    hashed_password = hashlib.md5(new_password.strip().encode('utf-8')).hexdigest()
    user = current_user
    user.password = hashed_password
    db.session.commit()

    # Xóa trạng thái xác thực OTP
    session.pop('otp_verified', None)

    return redirect(url_for("login_process"))