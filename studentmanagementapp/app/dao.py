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
        ClassroomTransfer.classroom_id == transcript.classroom_id,
        ClassroomTransfer.changed_classroom == False
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
        return True
    return False


def delete_score(score_id):
    score = Score.query.get(score_id)
    if score:
        db.session.delete(score)
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

    return new_score.id

def commit():
    db.session.commit()

def rollback():
    db.session.rollback()

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

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_subjects():
    return Subject.query.all()

def get_semesters(school_year_id=None):
    query = db.session.query(Semester.semester_type).distinct() \
        .join(SchoolYear, SchoolYear.id == Semester.school_year_id)
    if school_year_id:
        query = query.filter(SchoolYear.id == school_year_id)
    return query.all()

def get_school_years():
    return SchoolYear.query.all()

def get_summary_report(subject_id, semester_id):
    # Lấy thông tin semester để biết school_year_id
    semester = Semester.query.filter_by(id=semester_id).first()

    if not semester:
        return []  # Không có semester phù hợp

    school_year_id = semester.school_year_id

    # Trọng số cho từng loại điểm
    SCORE_WEIGHTS = {
        'FIFTEEN_MINUTE': 1,
        'ONE_PERIOD': 2,
        'EXAM': 3
    }

    # Tính điểm trung bình của từng học sinh cho từng loại điểm
    avg_score_subquery = db.session.query(
        Score.student_info_id.label('student_id'),  # ID học sinh
        func.avg(
            case(
                (Score.score_type == 'FIFTEEN_MINUTE', Score.score_number),
                else_=None
            )
        ).label('avg_fifteen_minute'),  # Trung bình điểm 15 phút
        func.avg(
            case(
                (Score.score_type == 'ONE_PERIOD', Score.score_number),
                else_=None
            )
        ).label('avg_one_period'),  # Trung bình điểm 1 tiết
        func.avg(
            case(
                (Score.score_type == 'EXAM', Score.score_number),
                else_=None
            )
        ).label('avg_exam'),  # Trung bình điểm thi
        Classroom.id.label('classroom_id')  # ID lớp học
    ).join(Transcript, Transcript.id == Score.transcript_id) \
        .join(Classroom, Classroom.id == Transcript.classroom_id) \
        .join(Curriculum, Curriculum.id == Transcript.curriculum_id) \
        .filter(
        Transcript.semester_id == semester_id,  # Lọc theo học kỳ
        Curriculum.subject_id == subject_id  # Lọc theo môn học
    ) \
        .group_by(Score.student_info_id, Classroom.id) \
        .subquery()

    # Tạo cột tính điểm trung bình tổng cho từng học sinh dựa trên trọng số
    total_avg_score = (
              (avg_score_subquery.c.avg_fifteen_minute * SCORE_WEIGHTS['FIFTEEN_MINUTE']) +
              (avg_score_subquery.c.avg_one_period * SCORE_WEIGHTS['ONE_PERIOD']) +
              (avg_score_subquery.c.avg_exam * SCORE_WEIGHTS['EXAM'])
      ) / sum(SCORE_WEIGHTS.values())  # Chia cho tổng trọng số
    # Query chính để tạo báo cáo
    query = db.session.query(
        Classroom.classroom_name.label('classroom_name'),  # Tên lớp
        Classroom.student_number.label('total_students'),  # Số học sinh trong lớp
        func.sum(
            case(
                (total_avg_score >= 5, 1),  # Đối với các học sinh đạt >= 5
                else_=0
            )
        ).label('passed_students'),  # Số học sinh đạt
        (func.sum(
            case(
                (total_avg_score >= 5, 1),
                else_=0
            )) / Classroom.student_number * 100).label('pass_rate')  # Tỷ lệ đạt
    ).join(
        avg_score_subquery, avg_score_subquery.c.classroom_id == Classroom.id
    ).join(
        Grade, Grade.id == Classroom.grade_id
    ).filter(
        Grade.school_year_id == school_year_id  # Lọc theo năm học
    ).group_by(Classroom.id)

    return query.all()

def get_students_by_classroom(classroom_id):
    try:
        # Truy vấn danh sách tên học sinh qua ApplicationForm
        students = db.session.query(StudentInfo).join(
            ClassroomTransfer, ClassroomTransfer.id == StudentInfo.application_form_id
        ).filter(
            ClassroomTransfer.classroom_id == classroom_id
        ).all()

        return students
    except Exception as e:
        print(f"Error in get_students_by_classroom: {e}")
        return []


# Trả về classroom của năm học
def get_classrooms_by_year_and_grade(school_year_name=None, classroom_name=None):
    classroom = (db.session.query(Classroom).join(
        Grade, Classroom.grade_id == Grade.id
    ).join(
        SchoolYear, SchoolYear.id == Grade.school_year_id)
    .filter(
        SchoolYear.school_year_name == school_year_name
    )).all()
    if classroom_name:
        classroom.filter(Classroom.classroom_name == classroom_name).first()
    return classroom

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


def get_classrooms_id_by_school_year_name_and_classroom_name(school_year_name, classroom_name):
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

def change_student_classroom(student_id):
    query  = ClassroomTransfer.query.filter(ClassroomTransfer.student_info_id == student_id,
                                            ClassroomTransfer.changed_classroom == False)
    return query(ClassroomTransfer.id).first()

def get_classroom_in_same_grade(classroom_id):
    same_grade_classrooms = (
        db.session.query(Classroom)
        .join(Grade, Classroom.grade_id == Grade.id)
        .filter(
            Classroom.grade_id == db.session.query(Classroom.grade_id).filter_by(id=classroom_id).scalar(),
            Classroom.id != classroom_id
        )
        .all()
    )
    return [{"id": c.id, "name": c.classroom_name} for c in same_grade_classrooms]


