import hashlib

from app import db, app
from app.admin import admin
from app.models import (SchoolYear, Semester, Grade, StudentInfo, ApplicationForm,
                        Subject, Curriculum, Transcript, Score, ClassroomTransfer, TeacherInfo,
                        ScoreType, Classroom, Gender, User, StaffInfo, Role, AdminInfo, Rule)
from faker import Faker
import random
from datetime import date

fake = Faker()


def generate_data():
    print("Starting to generate data...")
    try:
        # các quy định
        rules = [
            {"rule_name": "Độ tuổi tiếp nhận học sinh", "min_value": 15, "max_value": 20,
             "rule_content": "Học sinh có độ tuổi từ 15 đến 20 tuổi"},
            {"rule_name": "Số khối lớp", "min_value": 3, "max_value": 3,
             "rule_content": "Có 3 khối lớp (10, 11, 12)"},
            {"rule_name": "Số lớp tối thiểu mỗi khối", "min_value": 1, "max_value": None,
             "rule_content": "Mỗi khối có tối thiểu 1 lớp"},
            {"rule_name": "Số học sinh tối đa mỗi lớp", "min_value": None, "max_value": 40,
             "rule_content": "Mỗi lớp có tối đa 40 học sinh"},
            {"rule_name": "Số học kỳ mỗi năm", "min_value": 2, "max_value": 2,
             "rule_content": "Mỗi năm học có 2 học kỳ"},
            {"rule_name": "Số cột điểm 15 phút", "min_value": 1, "max_value": 5,
             "rule_content": "Từ 1 đến 5 cột điểm 15 phút"},
            {"rule_name": "Số bài kiểm tra 1 tiết", "min_value": 1, "max_value": 3,
             "rule_content": "Từ 1 đến 3 bài kiểm tra 1 tiết"},
            {"rule_name": "Số điểm thi cuối kỳ", "min_value": 1, "max_value": 1,
             "rule_content": "Có 1 điểm thi cuối kỳ"},
            {"rule_name": "Điểm trung bình đạt môn", "min_value": 5, "max_value": None,
             "rule_content": "Học sinh đạt môn nếu điểm trung bình >= 5"}
        ]

        # Thêm dữ liệu vào bảng Rule
        for rule_data in rules:
            rule = Rule(
                rule_name=rule_data["rule_name"],
                min_value=rule_data["min_value"],
                max_value=rule_data["max_value"],
                rule_content=rule_data["rule_content"]
            )
            db.session.add(rule)
        db.session.commit()
        print("Created rules.")

        # Tạo 3 năm học
        school_years = []
        for i in range(2):
            school_year_name = f"20{22 + i}-20{23 + i}"
            year = SchoolYear(school_year_name=school_year_name)
            db.session.add(year)
            school_years.append(year)
        db.session.commit()
        print("Created school years.")

        # Tạo học kỳ cho mỗi năm học
        semesters = []
        for year in school_years:
            for term in ["FIRST_TERM", "SECOND_TERM"]:
                semester = Semester(
                    semester_type=term,
                    school_year_id=year.id
                )
                db.session.add(semester)
                semesters.append(semester)
        db.session.commit()
        print("Created semesters.")

        # Tạo 3 khối cho mỗi năm học
        grades = []
        for year in school_years:
            for grade_type in ["GRADE_10", "GRADE_11", "GRADE_12"]:
                grade = Grade(
                    grade_type=grade_type,
                    school_year_id=year.id
                )
                db.session.add(grade)
                grades.append(grade)
        db.session.commit()
        print("Created grades.")

        # Tạo 3 lớp cho mỗi khối và thêm học sinh vào lớp chuyển lớp
        classrooms = []
        for grade in grades:
            for i in range(1, 3):  # 3 lớp mỗi khối
                classroom_name = f"{grade.grade_type.value}A{i}"
                classroom = Classroom(
                    classroom_name=classroom_name,
                    grade_id=grade.id
                )
                db.session.add(classroom)
                classrooms.append(classroom)
        db.session.commit()
        print("Created classrooms.")

        # Tạo học sinh và thêm vào bảng chuyển lớp
        all_students = []
        for classroom in classrooms:
            student_count = random.randint(35, 40)  # 35-40 học sinh mỗi lớp
            for _ in range(student_count):
                # Tạo ApplicationForm trước
                app_form = ApplicationForm(
                    name=fake.name(),
                    gender=random.choice([Gender.MALE, Gender.FEMALE]),
                    phone=fake.unique.phone_number()[:10],
                    address=fake.address(),
                    email=fake.unique.email(),
                    birthday=fake.date_of_birth(minimum_age=15, maximum_age=20),
                    status="ACCEPTED"
                )
                db.session.add(app_form)
                db.session.commit()

                # Tạo StudentInfo
                student = StudentInfo(
                    name=app_form.name,
                    gender=app_form.gender,
                    phone=app_form.phone,
                    address=app_form.address,
                    email=app_form.email,
                    birthday=app_form.birthday,
                    status=True,
                    application_form_id=app_form.id
                )
                db.session.add(student)
                db.session.commit()
                all_students.append(student)


                # Thêm học sinh vào bảng chuyển lớp
                transfer = ClassroomTransfer(
                    student_info_id=student.id,
                    classroom_id=classroom.id,
                    transfer_date=date.today(),
                    is_classroom_change=False
                )
                db.session.add(transfer)
                db.session.commit()

        print("Added students and updated class sizes.")

        # Tạo môn học
        subjects = ["Mathematics", "Literature", "Physics", "Chemistry", "Biology",
                    "History", "Geography", "English", "Civic Education", "Technology", "Informatics"]
        subject_list = []
        for subject_name in subjects:
            subject = Subject(subject_name=subject_name)
            db.session.add(subject)
            subject_list.append(subject)
        db.session.commit()
        print("Created subjects.")

        # Tạo chương trình học cho mỗi khối và môn học
        for grade in grades:
            for subject in subject_list:
                curriculum = Curriculum(
                    grade_id=grade.id,
                    subject_id=subject.id
                )
                db.session.add(curriculum)
        db.session.commit()
        print("Created curriculums.")

        num_staff=5
        num_teachers=15
        num_admins=3

        for _ in range(num_staff):
            # Tạo tài khoản nhân viên
            staff_user = User(
                username=fake.unique.user_name(),
                password=str(hashlib.md5("123456".strip().encode('utf-8')).hexdigest()),  # Mật khẩu mặc định
                role=Role.STAFF,
                avatar="https://res.cloudinary.com/dqw4mc8dg/image/upload/v1733391370/aj6sc6isvelwkotlo1vw.png"
            )
            db.session.add(staff_user)
            db.session.commit()  # Commit để lấy id cho user

            # Tạo thông tin nhân viên
            staff_info = StaffInfo(
                name=fake.name(),
                gender=random.choice([Gender.MALE, Gender.FEMALE]),
                phone=fake.unique.phone_number()[:10],
                address=fake.address(),
                email=fake.unique.email(),
                birthday=fake.date_of_birth(minimum_age=25, maximum_age=50),
                status=True,
                user_id=staff_user.id
            )
            db.session.add(staff_info)

            # Thêm giáo viên (Teacher)
        for _ in range(num_teachers):
            # Tạo tài khoản giáo viên
            teacher_user = User(
                username=fake.unique.user_name(),
                password=str(hashlib.md5("123456".strip().encode('utf-8')).hexdigest()),  # Mật khẩu mặc định
                role=Role.TEACHER,
                avatar="https://res.cloudinary.com/dqw4mc8dg/image/upload/v1733391370/aj6sc6isvelwkotlo1vw.png"
            )
            db.session.add(teacher_user)
            db.session.commit()  # Commit để lấy id cho user

            # Tạo thông tin giáo viên
            teacher_info = TeacherInfo(
                name=fake.name(),
                gender=random.choice([Gender.MALE, Gender.FEMALE]),
                phone=fake.unique.phone_number()[:10],
                address=fake.address(),
                email=fake.unique.email(),
                birthday=fake.date_of_birth(minimum_age=25, maximum_age=50),
                status=True,
                user_id=teacher_user.id
            )
            db.session.add(teacher_info)

            for _ in range(num_admins):
                # Tạo tài khoản admin
                admin_user = User(
                    username=fake.unique.user_name(),
                    password=str(hashlib.md5("123456".strip().encode('utf-8')).hexdigest()),  # Mật khẩu mặc định
                    role=Role.ADMIN,
                    avatar="https://res.cloudinary.com/dqw4mc8dg/image/upload/v1733391370/aj6sc6isvelwkotlo1vw.png"
                )
                db.session.add(admin_user)
                db.session.commit()  # Commit để lấy id cho user

                # Tạo thông tin nhân viên
                admin_info = AdminInfo(
                    name=fake.name(),
                    gender=random.choice([Gender.MALE, Gender.FEMALE]),
                    phone=fake.unique.phone_number()[:10],
                    address=fake.address(),
                    email=fake.unique.email(),
                    birthday=fake.date_of_birth(minimum_age=25, maximum_age=50),
                    status=True,
                    user_id=admin_user.id
                )
                db.session.add(admin_info)

            # Lưu tất cả dữ liệu vào database
        db.session.commit()
        print(f"Created admins, staff and teachers")

        # Tạo bảng điểm và nhập điểm cho học sinh
        teachers = TeacherInfo.query.all()
        for classroom in classrooms:
            for curriculum in Curriculum.query.filter_by(grade_id=classroom.grade_id).all():
                for semester in semesters:
                    teacher = random.choice(teachers)
                    transcript = Transcript(
                        classroom_id=classroom.id,
                        curriculum_id=curriculum.id,
                        semester_id=semester.id,
                        teacher_info_id=teacher.id
                    )
                    db.session.add(transcript)
                    db.session.commit()

                    students_in_class = StudentInfo.query.join(ClassroomTransfer).filter(
                        ClassroomTransfer.classroom_id == classroom.id
                    ).all()
                    for student in students_in_class:
                        for score_type in ScoreType:
                            score = Score(
                                score_number=round(random.uniform(4, 10), 1),
                                score_type=score_type,
                                student_info_id=student.id,
                                transcript_id=transcript.id
                            )
                            db.session.add(score)
        db.session.commit()
        print("Created transcripts and scores successfully.")

    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")


# Gọi hàm để tạo dữ liệu
with app.app_context():
    generate_data()
