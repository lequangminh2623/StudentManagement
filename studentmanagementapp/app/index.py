from flask import render_template, request, url_for, flash, session, redirect, jsonify
from app import dao, utils, login, app
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from app.models import Role, Transcript, Classroom, Curriculum, Subject, SchoolYear, Semester


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



# # Phân quyền
# @app.route('/teacher')
# @login_required
# def teacher():
#     if current_user.role not in [Role.ADMIN, Role.TEACHER, Role.STUDENT]:
#         return "Access denied!", 403
#     return "Welcome to the teacher page!"
#
#
# @app.route('/student')
# @login_required
# def student():
#     return "Welcome to the student page!"



@app.route("/transcripts", methods=['get', 'post'])
@login_required
def transcript_process():
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

                transcripts = dao.get_transcripts(teacher_info_id=teacher_info.id, school_year_id=school_year.id, semester_type=selected_semester, subject_name=selected_subject)
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

@app.route('/transcripts/<int:transcript_id>', methods=['GET'])
def score_process(transcript_id):
    student_scores = None
    transcript_data = None
    if request.method == 'GET':
        transcript_data = dao.get_transcripts(transcript_id=transcript_id)

        student_scores = dao.get_students_and_scores_by_transcript_id(transcript_id)


    return render_template('score.html', student_scores=student_scores, transcript_data=transcript_data)

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

@app.context_processor
def common_response():
    return {
        'Role': Role,
    }
