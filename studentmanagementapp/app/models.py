from email.policy import default

from faker import Faker
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Boolean, Enum, Date, UniqueConstraint, \
    CheckConstraint
from sqlalchemy.orm import relationship, declared_attr
from app import db, app, migrate
from enum import Enum as Enumerate
from flask_login import UserMixin
from datetime import date




class Role(Enumerate):
    ADMIN = 1
    STAFF = 2
    TEACHER = 3
    STUDENT = 4


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dqw4mc8dg/image/upload/w_1000,c_fill,ar_1:1,g_auto,r_max,bo_5px_solid_red,b_rgb:262c35/v1733391370/aj6sc6isvelwkotlo1vw.png')
    role = Column(Enum(Role), default=Role.STUDENT)
    admin_info = relationship("AdminInfo", back_populates="user", lazy=True)
    staff_info = relationship("StaffInfo", back_populates="user", lazy=True)
    teacher_info = relationship("TeacherInfo", back_populates="user", lazy=True)
    student_info = relationship("StudentInfo", back_populates="user", lazy=True)

    def __str__(self):
        return self.username


class UserInfo(db.Model):
    __abstract__ = True

    @declared_attr
    def name(cls):
        return Column(String(50), nullable=False)

    @declared_attr
    def gender(cls):
        return Column(Boolean, nullable=False)

    @declared_attr
    def phone(cls):
        return Column(String(10), unique=True, nullable=False)

    @declared_attr
    def address(cls):
        return Column(String(100), nullable=False)

    @declared_attr
    def email(cls):
        return Column(String(50), unique=True, nullable=False)

    @declared_attr
    def birthday(cls):
        return Column(Date, nullable=False)

    @declared_attr
    def status(cls):
        return Column(Boolean, nullable=False)

    @declared_attr
    def user_id(cls):
        return Column(Integer, ForeignKey(User.id, ondelete='SET NULL'), unique=True)

    @declared_attr
    def user(cls):
        return relationship(User, back_populates='user_info', lazy=True)

    def __str__(self):
        return self.name


class AdminInfo(UserInfo):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = relationship(User, back_populates="admin_info", lazy=True)


class StaffInfo(UserInfo):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = relationship(User, back_populates="staff_info", lazy=True)


class TeacherInfo(UserInfo):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = relationship(User, back_populates="teacher_info", lazy=True)


class SchoolYear(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    school_year_name = Column(String(50), unique=True, nullable=False)


class SemesterType(Enumerate):
    FIRSTTERM = 1
    SECONDTERM = 2


class Semester(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    semester_name = Column(Enum(SemesterType), nullable=False)
    school_year_id = Column(Integer, ForeignKey(SchoolYear.id, ondelete='RESTRICT'), nullable=False)
    school_year = relationship(SchoolYear, backref='semesters', lazy=True)

    __table_args__ = (
        UniqueConstraint('semester_name', 'school_year_id', name='uq_semestername_schoolyearid'),
    )

    def __str__(self):
        return self.semester_name


class GradeType(Enumerate):
    GRADE10 = 10
    GRADE11 = 11
    GRADE12 = 12


class Grade(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    grade_name = Column(Enum(GradeType), nullable=False)
    school_year_id = Column(Integer, ForeignKey(SchoolYear.id, ondelete='RESTRICT'), nullable=False)
    school_year = relationship(SchoolYear, backref='grades', lazy=True)

    __table_args__ = (
        UniqueConstraint('grade_name', 'school_year_id', name='uq_gradename_schoolyearid'),
    )

    def __str__(self):
        return self.grade_name


class Classroom(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    classroom_name = Column(String(50), nullable=False)
    student_number = Column(Integer, nullable=False, default=0)
    grade_id = Column(ForeignKey(Grade.id, ondelete='RESTRICT'), nullable=False)
    grade = relationship(Grade, backref='classrooms', lazy=True)

    __table_args__ = (
        UniqueConstraint('classroom_name', 'grade_id', name='uq_classroomname_gradeid'),
    )

    def __str__(self):
        return self.classroom_name


class ApplicationFormStatus(Enumerate):
    PENDING = 1
    ACCEPTED = 2
    REJECTED = 3


class ApplicationForm(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    gender = Column(Boolean, nullable=False)
    phone = Column(String(10), unique=True, nullable=False)
    address = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    birthday = Column(Date, nullable=False)
    status = Column(Enum(ApplicationFormStatus), default=ApplicationFormStatus.PENDING, nullable=False)

    def __str__(self):
        return self.name


class StudentInfo(UserInfo):
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_form_id = Column(Integer, ForeignKey(ApplicationForm.id, ondelete='SET NULL'), unique=True)
    application_form = relationship(ApplicationForm, backref='student_info', lazy=True)
    user = relationship("User", back_populates="student_info", lazy=True)


class Subject(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_name = Column(String(50), nullable=False, unique=True)

    def __str__(self):
        return self.subject_name


class Curriculum(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    curriculum_name = Column(String(50), nullable=False)
    grade_id = Column(Integer, ForeignKey(Grade.id, ondelete='CASCADE'), nullable=False)
    grade = relationship(Grade, backref='curriculums', lazy=True)
    subject_id = Column(Integer, ForeignKey(Subject.id, ondelete='CASCADE'), nullable=False)
    subject = relationship(Subject, backref='curriculums', lazy=True)

    __table_args__ = (
        UniqueConstraint('grade_id', 'subject_id', name='uq_gradeid_subjectid'),
    )

    def __str__(self):
        return self.curriculum_name


class Report(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_name = Column(String(50), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id, ondelete='CASCADE'), nullable=False)
    subject = relationship(Subject, backref='reports', lazy=True)
    semester_id = Column(Integer, ForeignKey(Semester.id, ondelete='CASCADE'), nullable=False)
    semester = relationship(Semester, backref='reports', lazy=True)

    __table_args__ = (
        UniqueConstraint('subject_id', 'semester_id', name='uq_subjectid_semesterid'),
    )

    def __str__(self):
        return self.report_name


class Statistic(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    pass_count = Column(Integer, nullable=False)
    pass_rate = Column(Float, nullable=False)
    classroom_id = Column(Integer, ForeignKey(Classroom.id, ondelete='CASCADE'), nullable=False)
    classroom = relationship(Classroom, backref='statistics', lazy=True)
    report_id = Column(Integer, ForeignKey(Report.id, ondelete='CASCADE'), nullable=False)
    report = relationship(Report, backref='statistics', lazy=False)

    __table_args__ = (
        UniqueConstraint('classroom_id', 'report_id', name='uq_classroomid_reportid'),
    )

    def __str__(self):
        return self.classroom


class Transcript(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    transcript_name = Column(String(50), nullable=False)
    is_done = Column(Boolean, nullable=False, default=False)
    classroom_id = Column(Integer, ForeignKey(Classroom.id, ondelete='CASCADE'), nullable=False)
    classroom = relationship(Classroom, backref='transcripts', lazy=True)
    curriculum_id = Column(Integer, ForeignKey(Curriculum.id, ondelete='RESTRICT'), nullable=False)
    curriculum = relationship(Curriculum, backref='transcripts', lazy=True)
    semester_id = Column(Integer, ForeignKey(Semester.id, ondelete='RESTRICT'), nullable=False)
    semester = relationship(Semester, backref='transcripts', lazy=True)
    teacher_info_id = Column(Integer, ForeignKey(TeacherInfo.id, ondelete='RESTRICT'), nullable=False)
    teacher_info = relationship(TeacherInfo, backref='transcripts', lazy=True)

    fifteenminutescores = relationship("FifteenMinuteScore", back_populates="transcript", lazy=True)
    oneperiodscores = relationship("OnePeriodScore", back_populates="transcript", lazy=True)
    examscores = relationship("ExamScore", back_populates="transcript", lazy=True)
    firsttermaveragescores = relationship("FirstTermAverageScore", back_populates="transcript", lazy=True)
    secondtermaveragescores = relationship("SecondTermAverageScore", back_populates="transcript", lazy=True)

    __table_args__ = (
        UniqueConstraint('classroom_id', 'curriculum_id', 'semester_id', name='uq_classroomid_curriculumid_semesterid'),
    )

    def __str__(self):
        return self.transcript_name


class ScoreColumn(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    score = Column(Float, CheckConstraint('score >= 0 AND score <= 10'), nullable=True)
    weight = Column(Integer, nullable=False)
    score_column_name = Column(String(50), nullable=False)
    transcript_id = Column(Integer, ForeignKey(Transcript.id, ondelete='RESTRICT'), nullable=False)

    @declared_attr
    def transcript(cls):
        return relationship(Transcript, back_populates=f"{cls.__name__.lower()}s", lazy=False)

    def __str__(self):
        return self.score_column_name


class FifteenMinuteScore(ScoreColumn):
    weight = 1
    score_column_name = "Fifteen Minute Score"
    student_info_id = Column(Integer, ForeignKey(StudentInfo.id, ondelete='CASCADE'), nullable=False)
    student_info = relationship(StudentInfo, backref="fifteen_minute_scores", lazy=True)


class OnePeriodScore(ScoreColumn):
    weight = 2
    score_column_name = "One Period Score"
    student_info_id = Column(Integer, ForeignKey(StudentInfo.id, ondelete='CASCADE'), nullable=False)
    student_info = relationship(StudentInfo, backref="one_period_scores", lazy=True)


class ExamScore(ScoreColumn):
    weight = 3
    score_column_name = "Exam Score"
    student_info_id = Column(Integer, ForeignKey(StudentInfo.id, ondelete='CASCADE'), nullable=False)
    student_info = relationship(StudentInfo, backref="exam_scores", lazy=True)


class FirstTermAverageScore(ScoreColumn):
    weight = 1
    score_column_name = "First Term Average Score"
    student_info_id = Column(Integer, ForeignKey(StudentInfo.id, ondelete='CASCADE'), nullable=False)
    student_info = relationship(StudentInfo, backref="first_term_average_scores", lazy=True)


class SecondTermAverageScore(ScoreColumn):
    weight = 2
    score_column_name = "Second Term Average Score"
    student_info_id = Column(Integer, ForeignKey(StudentInfo.id, ondelete='CASCADE'), nullable=False)
    student_info = relationship(StudentInfo, backref="second_term_average_scores", lazy=True)


class ClassroomTransfer(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_classroom_changed = Column(Boolean, nullable=False, default=False)
    transfer_date = Column(Date, nullable=False, default=date.today)
    classroom_id = Column(Integer, ForeignKey(Classroom.id, ondelete='RESTRICT'), nullable=False)
    classroom = relationship(Classroom, backref='classroom_transfers', lazy=True)
    student_info_id = Column(Integer, ForeignKey(StudentInfo.id, ondelete='CASCADE'), nullable=False)
    student_info = relationship(StudentInfo, backref='classroom_transfers', lazy=True)

    __table_args__ = (
        UniqueConstraint('student_info_id', 'classroom_id', 'transfer_date', name='uq_studentinfoid_classroom_transferdate'),
    )


class Rule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(50), unique=True, nullable=False)
    min_value = Column(Integer)
    max_value = Column(Integer)
    rule_content = Column(String(500), unique=True, nullable=False)

    def __str__(self):
        return self.score_column_name


# op.execute("""
#     CREATE TRIGGER check_grade_insert
#     BEFORE INSERT ON grade
#     FOR EACH ROW
#     BEGIN
#         DECLARE count_grade INT;
#
#         -- Lấy số lượng khối lớp hiện tại của năm học
#         SELECT COUNT(DISTINCT grade_name)
#         INTO count_grade
#         FROM grade
#         WHERE school_year_id = NEW.school_year_id;
#
#         -- Kiểm tra nếu vượt quá 3 khối lớp
#         IF count_grade >= 3 THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Can not add. School year already have 3 grades.';
#         END IF;
#     END;
#     """)
#
#     op.execute("""
#     CREATE TRIGGER check_grade_delete
#     BEFORE DELETE ON grade
#     FOR EACH ROW
#     BEGIN
#         SIGNAL SQLSTATE '45000'
#         SET MESSAGE_TEXT = 'Can not delete. School year must has at least 3 semester.';
#     END;
#     """)
#
#     op.execute("""
#     CREATE TRIGGER check_max_student
#     BEFORE INSERT ON classroom_transfer
#     FOR EACH ROW
#     BEGIN
#         DECLARE student_count INT;
#         DECLARE max_count INT;
#
#         -- Lấy số lượng học sinh hiện tại trong lớp
#         SELECT COUNT(*) INTO student_count
#         FROM class_transfer
#         WHERE lop_hoc_id = NEW.lop_hoc_id;
#
#         -- Lấy giới hạn học sinh của lớp từ bảng LopHoc
#         SELECT max_value INTO max_count
#         FROM rule
#         WHERE id = 4;
#
#         -- Nếu không có giới hạn, mặc định là 40
#         IF max_count IS NULL THEN
#             SET max_count = 40;
#         END IF;
#
#         -- Kiểm tra nếu lớp đã đủ số học sinh theo giới hạn
#         IF student_count >= max_count THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Classroom reached max student number.';
#         END IF;
#     END;
#     """)
#
#     op.execute("""
#     CREATE TRIGGER check_semester
#     BEFORE INSERT ON semester
#     FOR EACH ROW
#     BEGIN
#         DECLARE semester_count INT;
#         DECLARE existed_semester INT;
#
#         -- Đếm số học kỳ trong năm học hiện tại
#         SELECT COUNT(*) INTO semester_count
#         FROM semester
#         WHERE school_year_id = NEW.school_year_id;
#
#         -- Nếu năm học đã có 2 học kỳ, không cho phép thêm học kỳ thứ 3
#         IF semester_count >= 2 THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'School year already has 2 semesters.';
#         END IF;
#
#         -- Kiểm tra xem cả hai học kỳ HK1 và HK2 đã có trong năm học chưa
#         IF NEW.ten_semester = 'FIRSTTERM' OR NEW.ten_semester = 'SECONDTERM' THEN
#             SELECT COUNT(*) INTO existed_semester
#             FROM semester
#             WHERE school_year_id = NEW.school_year_id
#               AND (ten_semester = 'FIRSTTERM' OR ten_semester = 'SECONDTERM');
#
#             -- Nếu cả hai học kỳ HK1 và HK2 chưa tồn tại, cho phép thêm
#             IF existed_semester >= 2 THEN
#                 SIGNAL SQLSTATE '45000'
#                 SET MESSAGE_TEXT = 'Năm học này đã có đủ 2 học kỳ (HK1 và HK2).';
#             END IF;
#         END IF;
#     END;
#     """)




if __name__ == '__main__':
    with app.app_context():
        # namhoc=SchoolYear(school_year_name='2020-2021')
        # db.session.add(namhoc)
        #
        # hocky1 = Semester(semester_name=SemesterType.FIRSTTERM, school_year_id=1)
        # db.session.add(hocky1)
        # hocky2 = Semester(semester_name=SemesterType.SECONDTERM, school_year_id=1)
        # db.session.add(hocky2)
        #
        # khoi10 = Grade(grade_name=GradeType.GRADE10, school_year_id=1)
        # db.session.add(khoi10)
        # khoi11 = Grade(grade_name=GradeType.GRADE11, school_year_id=1)
        # db.session.add(khoi11)
        # khoi12 = Grade(grade_name=GradeType.GRADE12, school_year_id=1)
        # db.session.add(khoi12)

        # lop10A1 = Classroom(classroom_name='10A1', grade_id=1)
        # db.session.add(lop10A1)
        # lop10A2 = Classroom(classroom_name='10A2', grade_id=1)
        # db.session.add(lop10A2)

        # fake = Faker()
        # fake_name = fake.name()
        # fake_gender = fake.boolean()
        # fake_phone = fake.unique.phone_number()[:10]
        # fake_address = fake.address()
        # fake_email = fake.unique.email()
        # fake_birthday = fake.date_between(start_date="-20y", end_date="-15y")
        # fake_status = True
        #
        # # user = User(username=fake.user_name(), password=fake.password())
        # # db.session.add(user)
        # # db.session.commit()
        #
        # hocsinh = StudentInfo(
        #     name=fake_name,
        #     gender=fake_gender,
        #     phone=fake_phone,
        #     address=fake_address,
        #     email=fake_email,
        #     birthday=fake_birthday,
        #     status=fake_status,
        # )
        # db.session.add(hocsinh)



        db.session.commit()