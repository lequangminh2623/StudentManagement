from flask import render_template, request, url_for, flash, session, redirect
from app import dao, utils, login, app
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from app.models import Role


@app.route("/")
def index():
    return render_template('index.html')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/login", methods=['GET', 'POST'])
def login_process():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.', 'error')
            return render_template('login.html')

        user = dao.check_user(username, password)
        if user:
            login_user(user)
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role.name

            user_role = dao.get_user_role(user.role)

            if current_user.role.name in ("admin", "staff"):
                return redirect(url_for("admin.index"))

            return redirect('/')
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')

    return render_template('login.html')

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


# Phân quyền
@app.route('/teacher')
@login_required
def teacher():
    if current_user.role not in [Role.ADMIN, Role.TEACHER, Role.STUDENT]:
        return "Access denied!", 403
    return "Welcome to the teacher page!"


@app.route('/student')
@login_required
def student():
    return "Welcome to the student page!"


from datetime import datetime


@app.route("/score", methods=['get', 'post'])
@login_required
def score_input():
    school_years = dao.get_school_years()
    #
    # # Lấy năm học gần nhất
    latest_school_year = None
    # if school_years:
    #     latest_school_year = max(school_years, key=lambda sy: int(sy.school_year_name.split('-')[0]))
    #
    semesters = [
        {"id": 1, "name": "FIRST_TERM"},
        {"id": 2, "name": "SECOND_TERM"}
    ]
    #
    classrooms = []
    subjects = []
    #
    # if current_user.role == Role.TEACHER and latest_school_year:
    #     teacher_info = dao.get_teacher_info_by_user_id(current_user.id)
    #     if teacher_info:
    #         # Lấy các bảng điểm của giáo viên trong năm học gần nhất
    #         transcripts = dao.get_transcripts_by_teacher_and_school_year(teacher_info.id, latest_school_year.id)
    #
    #         classroom_ids = set()
    #         subject_ids = set()
    #
    #         for transcript in transcripts:
    #             classroom_ids.add(transcript.classroom_id)
    #             subject_ids.add(transcript.curriculum.subject_id)
    #
    #         classrooms = [dao.get_classroom_by_id(id) for id in classroom_ids if dao.get_classroom_by_id(id) is not None]
    #         subjects = [dao.get_subject_by_id(id) for id in subject_ids if dao.get_subject_by_id(id) is not None]

    filters = [
        {"name": "School Year", "id": "school-year", "data": school_years},
        {"name": "Semester", "id": "semester", "data": semesters},
        {"name": "Classroom", "id": "classroom", "data": classrooms},
        {"name": "Subject", "id": "subject", "data": subjects}
    ]

    return render_template('score.html', filters=filters, latest_school_year=latest_school_year)


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.context_processor
def common_response():
    return {
        'Role': Role,
        'current_year': datetime.now().year
    }