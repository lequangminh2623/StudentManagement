from sqlalchemy import func, case, cast
from app.models import *
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
    transcript = Transcript.query.filter_by(id=transcript_id).first()
    if not transcript:
        return []

    students = db.session.query(
        StudentInfo.id.label('student_id'),
        StudentInfo.name.label('student_name'),
        Score.score_number.label('score'),
        Score.score_type.label('score_type'),
        Score.id.label('score_id')
    ).outerjoin(
        Score, (Score.student_info_id == StudentInfo.id) & (Score.transcript_id == transcript_id)
    ).join(
        ClassroomTransfer, ClassroomTransfer.student_info_id == StudentInfo.id
    ).filter(
        ClassroomTransfer.classroom_id == transcript.classroom_id
    ).all()

    student_scores = {}
    for student in students:
        if student.student_id not in student_scores:
            student_scores[student.student_id] = {
                'student_id': student.student_id,
                'student_name': student.student_name,
                'FIFTEEN_MINUTE': [],  # Danh sách điểm 15 phút
                'ONE_PERIOD': [],      # Danh sách điểm 1 tiết
                'EXAM': []            # Danh sách điểm thi
            }

        if student.score is not None:
            score_type = student.score_type.name
            score_data = {
                'score_id': student.score_id,
                'score': student.score,
            }
            student_scores[student.student_id][score_type].append(score_data) # Lưu trực tiếp vào danh sách

    return list(student_scores.values())


def update_score(score_id, new_value):
    score = Score.query.get(score_id)
    if score:
        score.score_number = new_value
        db.session.commit()
        return True
    return False


def delete_score(score_id):
    score = Score.query.get(score_id)
    if score:
        db.session.delete(score)
        db.session.commit()
        return True
    return False


def create_score(student_info_id, transcript_id, score_type, score_value):
    new_score = Score(
        score_number=score_value,
        score_type=score_type,
        student_info_id=student_info_id,
        transcript_id=transcript_id
    )
    db.session.add(new_score)
    db.session.commit()
    return new_score.id

def get_transcript_avg(transcript_id):
    transcript = Transcript.query.get(transcript_id)
    if not transcript:
        return None  # Hoặc xử lý lỗi tùy theo ứng dụng

    school_year_name = transcript.semester.school_year.school_year_name
    classroom_name = transcript.classroom.classroom_name

    student_scores = db.session.query(
        StudentInfo.name,
        Semester.semester_type,
        func.avg(Score.score_number).label('average_score')
    ).join(Score, Score.student_info_id == StudentInfo.id)\
    .join(Transcript, Transcript.id == Score.transcript_id)\
    .join(Semester, Semester.id == Transcript.semester_id)\
    .filter(Transcript.classroom_id == transcript.classroom_id)\
    .group_by(StudentInfo.name, Semester.semester_type)\
    .all()

    result = []
    for student_name, semester_type, average_score in student_scores:
        student_data = next((item for item in result if item['student_info_name'] == student_name), None)
        if not student_data:
            student_data = {'student_info_name': student_name, 'average_score_semester_1': None, 'average_score_semester_2': None}
            result.append(student_data)

        if semester_type == SemesterType.FIRST_TERM:
            student_data['average_score_semester_1'] = round(average_score, 1)
        elif semester_type == SemesterType.SECOND_TERM:
            student_data['average_score_semester_2'] = round(average_score, 1)

    final_result = {
        'school_year_name': school_year_name,
        'classroom_name': classroom_name,
        'student_scores': result
    }
    return final_result

def diem_stats(semester_id=None, subject_id=None):
    query = db.session.query(
        Score.score_number.label('score'),
        func.count(Score.student_info_id).label('student_count')
    ).join(Transcript, Transcript.id == Score.transcript_id) \
     .join(Curriculum, Curriculum.id == Transcript.curriculum_id) \
     .join(Semester, Semester.id == Transcript.semester_id)

    if semester_id:
        query = query.filter(Semester.id == semester_id)

    if subject_id:
        query = query.filter(Curriculum.subject_id == subject_id)

    return query.group_by(Score.score_number).order_by(Score.score_number.asc()).all()


def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_subjects():
    return Subject.query.all()

def get_semesters():
    return db.session.query(Semester.semester_type).distinct().all()

def get_school_years():
    return SchoolYear.query.all()

def get_summary_report(subject_id, semester_id):
    query = db.session.query(
        Classroom.classroom_name.label('classroom_name'),
        func.count(Score.student_info_id).label('total_students'),
        func.sum(case((Score.score_number >= 5, 1), else_=0)).label('passed_students'),
        (func.sum(case((Score.score_number >= 5, 1), else_=0)) / func.count(Score.student_info_id) * 100).label(
            'pass_rate')
    ).join(Transcript, Transcript.id == Score.transcript_id) \
        .join(Classroom, Classroom.id == Transcript.classroom_id) \
        .filter(Transcript.curriculum.has(subject_id=subject_id), Transcript.semester_id == semester_id) \
        .group_by(Classroom.classroom_name) \


    return query.all()

