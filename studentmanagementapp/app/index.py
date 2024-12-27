from flask import render_template, request, url_for,session, redirect
from app import dao, utils, login, app
from flask_login import login_user, login_required, logout_user, current_user
from app.models import Role


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
    filters = []
    transcript_data = []
    if current_user.role != Role.TEACHER:
        session['errors'] = ["Unauthorized"]
    else:
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
    transcript_info = None
    transcript = None
    if current_user.role != Role.TEACHER:
        session['errors'] = ["Unauthorized"]

    else:
        transcript_info = dao.get_transcripts(transcript_id=transcript_id)
        transcript = dao.get_students_and_scores_by_transcript_id(transcript_id)
        if not transcript or not transcript_info:
            session['errors'] = ["Can not find any transcript."]

        if request.method == 'POST':
            form_data = request.form
            updated_scores = []
            new_scores = []
            deleted_scores = []
            errors = []

            for key, value in form_data.items():
                value = value.strip()
                student_id_str, score_id_str, score_type, index = key.split('-')
                student_id = int(student_id_str)
                score_id = int(score_id_str) if score_id_str != 'new' else 'new'

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
                    for student in transcript:
                        if student['student_id'] == student_id:
                            original_scores = student.get(score_type, [])
                            original_score = next((s for s in original_scores if s.get('score_id') == score_id), None)

                            if original_score:
                                if score_number is None:
                                    deleted_scores.append(score_id)
                                elif original_score.get('score') != score_number:
                                    updated_scores.append({
                                        'score_id': score_id,
                                        'score_number': score_number
                                    })
                            break

            if errors:
                session['errors'] = errors
            try:
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
                dao.commit()
                session['messages'] = ["Successfully Updated!"]
            except Exception as db_error:
                dao.rollback()
                session['errors'] = [f"Minimum and maximum score violation: {db_error}"]
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
    transcript_data = None
    if current_user.role != Role.TEACHER:
        session['errors'] = ["Unauthorized"]
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
