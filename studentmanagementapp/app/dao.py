from sqlalchemy.sql.operators import contains

from app import app
import hashlib

from app.models import *


# from models import User


# def auth_user(username, password):
#     password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
#
#     return User.query.filter(User.username.__eq__(username),
#                              User.password.__eq__(password)).first()

# def get_user_by_id(id):
#     return User.query.get(id)

def get_school_years():
    return SchoolYear.query.all()

def get_classrooms():
    return Classroom.query.all()

def get_subjects():
    return Subject.query.all()

def get_teacher_info_by_user_id(user_id):
    """Lấy thông tin giáo viên dựa trên user_id."""
    user = User.query.get(user_id)
    if user and user.role == Role.TEACHER:
        return TeacherInfo.query.filter_by(user_id=user_id).first()
    return None

def get_transcripts_by_teacher_and_school_year(teacher_info_id, school_year_id):
    """Lấy các bảng điểm của giáo viên trong một năm học cụ thể."""
    return Transcript.query.join(Transcript.classroom).join(Classroom.grade).join(Grade.school_year).filter(
        Transcript.teacher_info_id == teacher_info_id,
        Grade.school_year_id == school_year_id
    ).all()

def get_classroom_by_id(classroom_id):
    """Lấy lớp học theo ID."""
    return Classroom.query.get(classroom_id)

def get_subject_by_id(subject_id):
    """Lấy môn học theo ID."""
    return Subject.query.get(subject_id)

# Các hàm khác có thể cần
def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_grade_by_school_year_and_grade_type(school_year_id, grade_type):
    return Grade.query.filter_by(school_year_id = school_year_id, grade_type = grade_type).first()

def get_semester_by_school_year_and_semester_type(school_year_id, semester_type):
    return Semester.query.filter_by(school_year_id = school_year_id, semester_type = semester_type).first()

def get_curriculum_by_grade_and_subject(grade_id, subject_id):
    return Curriculum.query.filter_by(grade_id = grade_id, subject_id = subject_id).first()

def get_student_info_by_user_id(user_id):
    user = User.query.get(user_id)
    if user and user.role == Role.STUDENT:
        return StudentInfo.query.filter_by(user_id=user_id).first()
    return None