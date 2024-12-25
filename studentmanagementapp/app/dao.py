from sqlalchemy import func
from sqlalchemy.sql.operators import contains
from app.models import *
from app import app
import hashlib

def check_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username),
                              User.password.__eq__(password)).first()

def get_user_role(role):
    if isinstance(role, Role):
        return role.name.lower()
    return None

def get_user_id(user_id):
    return User.query.filter(User.id.__eq__(user_id)).first()

def get_current_school_year():
    return SchoolYear.query.order_by(-SchoolYear.id).first()

def get_subject_names_by_teacher(teacher_info_id, school_year_id):
    query = db.session.query(Subject.subject_name) \
        .join(Curriculum, Curriculum.subject_id == Subject.id) \
        .join(Transcript, Transcript.curriculum_id == Curriculum.id) \
        .join(Classroom, Classroom.id == Transcript.classroom_id) \
        .join(Grade, Grade.id == Classroom.grade_id) \
        .join(SchoolYear, SchoolYear.id == Grade.school_year_id) \
        .filter(Transcript.teacher_info_id == teacher_info_id) \
        .filter(SchoolYear.id == school_year_id) \
        .distinct()

    return [subject[0] for subject in query.all()]

def get_teacher(user_id=None):
    query = TeacherInfo.query
    if user_id:
        query = query.filter(TeacherInfo.user_id==user_id)

    return query.first()

from sqlalchemy import and_

def get_transcripts(transcript_id=None, teacher_info_id=None, school_year_id=None, semester_type=None, subject_name=None):
    if transcript_id:
        query = db.session.query(
            Classroom.classroom_name,
            Subject.subject_name,
            Semester.semester_type,
            SchoolYear.school_year_name
        ).select_from(Transcript) \
            .join(Curriculum, Curriculum.id == Transcript.curriculum_id) \
            .join(Subject, Subject.id == Curriculum.subject_id) \
            .join(Semester, Semester.id == Transcript.semester_id) \
            .join(Classroom, Classroom.id == Transcript.classroom_id) \
            .join(Grade, Grade.id == Classroom.grade_id) \
            .join(SchoolYear, SchoolYear.id == Grade.school_year_id) \
            .filter(Transcript.id == transcript_id)
        return query.first()

    else:
        query = db.session.query(
            SchoolYear.school_year_name,
            Semester.semester_type,
            Classroom.classroom_name,
            Subject.subject_name,
            Transcript.id
        ).select_from(Transcript) \
            .join(Curriculum, Curriculum.id == Transcript.curriculum_id) \
            .join(Subject, Subject.id == Curriculum.subject_id) \
            .join(Semester, Semester.id == Transcript.semester_id) \
            .join(Classroom, Classroom.id == Transcript.classroom_id) \
            .join(Grade, Grade.id == Classroom.grade_id) \
            .join(SchoolYear, SchoolYear.id == Grade.school_year_id) \
            .filter(and_( # Use and_ for multiple conditions
                Transcript.teacher_info_id == teacher_info_id,
                SchoolYear.id == school_year_id,
                Semester.semester_type == semester_type,
                Subject.subject_name == subject_name
            ))
        return query.all()


def get_students_and_scores_by_transcript_id(transcript_id):
    # Truy vấn bảng điểm
    transcript = Transcript.query.filter_by(id=transcript_id).first()
    if not transcript:
        return []

    # Truy vấn danh sách học sinh thông qua ClassroomTransfer
    students = db.session.query(
        StudentInfo.id.label('student_id'),
        StudentInfo.name.label('student_name'),
        Score.score_number.label('score'),
        Score.score_type.label('score_type')
    ).outerjoin(
        Score, (Score.student_info_id == StudentInfo.id) & (Score.transcript_id == transcript_id)
    ).join(
        ClassroomTransfer, ClassroomTransfer.student_info_id == StudentInfo.id
    ).filter(
        ClassroomTransfer.classroom_id == transcript.classroom_id
    ).all()

    # Xử lý dữ liệu để gom nhóm theo học sinh và phân loại điểm
    student_scores = {}
    for student in students:
        if student.student_id not in student_scores:
            student_scores[student.student_id] = {
                'student_id': student.student_id,
                'student_name': student.student_name,
                'scores': {
                    'FIFTEEN_MINUTE': [],
                    'ONE_PERIOD': [],
                    'EXAM': []
                }
            }

        # Thêm điểm vào loại phù hợp nếu có
        if student.score is not None:
            score_type = student.score_type.name
            if score_type in student_scores[student.student_id]['scores']:
                student_scores[student.student_id]['scores'][score_type].append(student.score)

    return list(student_scores.values())



def get_user_by_id(user_id):
    return User.query.get(user_id)