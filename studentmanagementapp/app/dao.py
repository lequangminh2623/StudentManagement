from sqlalchemy import func, case
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


def diem_stats(semester_id=None, subject_id=None):
    query = db.session.query(
        Score.score_number.label('score'),  # Cột điểm
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

def get_classrooms():
    return Classroom.query.all()

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
        .all()

    return query

def get_students_by_classroom(classroom_id):
    try:
        # Truy vấn danh sách tên học sinh qua ApplicationForm
        students = db.session.query(ApplicationForm).join(
            StudentInfo, StudentInfo.application_form_id == ApplicationForm.id
        ).join(
            ClassroomTransfer, ClassroomTransfer.id == StudentInfo.application_form_id
        ).filter(
            ClassroomTransfer.classroom_id == classroom_id
        ).all()

        return students
    except Exception as e:
        print(f"Error in get_students_by_classroom: {e}")
        return []


def get_classrooms_by_year_and_grade(school_year_name, classroom_name):
    classroom = (db.session.query(Classroom).join(
        Grade, Classroom.grade_id == Grade.id
    ).join(
        SchoolYear, SchoolYear.id == Grade.school_year_id)
    .filter(
        SchoolYear.school_year_name == school_year_name,
        Classroom.classroom_name == classroom_name
    ).first())  # Dùng first() để lấy 1 lớp đầu tiên nếu tìm thấy
    if classroom:
        return classroom.id
    else:
        return None

def get_classroom_and_student_count(classroom_id):
    try:
        classroom = db.session.query(Classroom).filter(Classroom.id == classroom_id).first()
        return classroom.student_number
    except Exception as e:
        print(f"Error in get_total_students_by_classroom: {e}")
        return 0

def get_student_info_by_id(student_info_id):
    return db.session.query(StudentInfo).filter(StudentInfo.id == student_info_id).first()

def delete_student_by_id(student_info_id):
    # Tìm học sinh theo ID
    student = StudentInfo.query.get(student_info_id)
    if student:
        # Xóa học sinh khỏi cơ sở dữ liệu
        db.session.delete(student)
        db.session.commit()
        return {"success": True, "message": "Xóa học sinh thành công"}
    else:
        return {"success": False, "message": "Không tìm thấy học sinh"}