import hashlib

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
    avatar = Column(String(255),
                    default='https://res.cloudinary.com/dqw4mc8dg/image/upload/w_1000,c_fill,ar_1:1,g_auto,r_max,bo_5px_solid_red,b_rgb:262c35/v1733391370/aj6sc6isvelwkotlo1vw.png')
    role = Column(Enum(Role), default=Role.STUDENT)

    def __str__(self):
        return self.username


class Gender(Enumerate):
    MALE = 1
    FEMALE = 2


class UserInfo(db.Model):
    __abstract__ = True

    @declared_attr
    def name(cls):
        return Column(String(50), nullable=False)

    @declared_attr
    def gender(cls):
        return Column(Enum(Gender), nullable=False)

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


    def __str__(self):
        return self.name


class AdminInfo(UserInfo):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = relationship(User, backref="admin_info", lazy=True)


class StaffInfo(UserInfo):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = relationship(User, backref="staff_info", lazy=True)


class TeacherInfo(UserInfo):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = relationship(User, backref="teacher_info", lazy=True)


class SchoolYear(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    school_year_name = Column(String(50), unique=True, nullable=False)

    def __str__(self):
        return self.school_year_name


class SemesterType(Enumerate):
    FIRST_TERM = 1
    SECOND_TERM = 2


class Semester(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    semester_type = Column(Enum(SemesterType), nullable=False)
    school_year_id = Column(Integer, ForeignKey(SchoolYear.id, ondelete='RESTRICT'), nullable=False)
    school_year = relationship(SchoolYear, backref='semesters', lazy=True)

    __table_args__ = (
        UniqueConstraint('semester_type', 'school_year_id', name='uq_semestertype_schoolyearid'),
    )

    def __str__(self):
        return self.semester_type.name


class GradeType(Enumerate):
    GRADE_10 = 1
    GRADE_11 = 2
    GRADE_12 = 3


class Grade(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    grade_type = Column(Enum(GradeType), nullable=False)
    school_year_id = Column(Integer, ForeignKey(SchoolYear.id, ondelete='RESTRICT'), nullable=False)
    school_year = relationship(SchoolYear, backref='grades', lazy=True)

    __table_args__ = (
        UniqueConstraint('grade_type', 'school_year_id', name='uq_gradetype_schoolyearid'),
    )

    def __str__(self):
        return self.grade_type.name


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
    gender = Column(Enum(Gender), nullable=False)
    phone = Column(String(10), unique=True, nullable=False)
    address = Column(String(100), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    birthday = Column(Date, nullable=False)
    status = Column(Enum(ApplicationFormStatus), default=ApplicationFormStatus.PENDING, nullable=False)

    def __str__(self):
        return self.name


class StudentInfo(UserInfo):
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_form_id = Column(Integer, ForeignKey(ApplicationForm.id, ondelete='SET NULL'), unique=True)
    application_form = relationship(ApplicationForm, lazy=True)
    user = relationship("User", backref="student_info", lazy=True)


class Subject(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_name = Column(String(50), nullable=False, unique=True)

    def __str__(self):
        return self.subject_name


class Curriculum(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    grade_id = Column(Integer, ForeignKey(Grade.id, ondelete='CASCADE'), nullable=False)
    grade = relationship(Grade, backref='curriculums', lazy=True)
    subject_id = Column(Integer, ForeignKey(Subject.id, ondelete='CASCADE'), nullable=False)
    subject = relationship(Subject, backref='curriculums', lazy=True)

    __table_args__ = (
        UniqueConstraint('grade_id', 'subject_id', name='uq_gradeid_subjectid'),
    )

    def __str__(self):
        return f'{str(self.subject)}-{str(self.grade)}-{str(self.grade.school_year)}'


class Transcript(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_done = Column(Boolean, nullable=False, default=False)
    classroom_id = Column(Integer, ForeignKey(Classroom.id, ondelete='CASCADE'), nullable=False)
    classroom = relationship(Classroom, backref='transcripts', lazy=True)
    curriculum_id = Column(Integer, ForeignKey(Curriculum.id, ondelete='RESTRICT'), nullable=False)
    curriculum = relationship(Curriculum, lazy=False)
    semester_id = Column(Integer, ForeignKey(Semester.id, ondelete='RESTRICT'), nullable=False)
    semester = relationship(Semester, backref='transcripts', lazy=True)
    teacher_info_id = Column(Integer, ForeignKey(TeacherInfo.id, ondelete='RESTRICT'), nullable=False)
    teacher_info = relationship(TeacherInfo, backref='transcripts', lazy=True)

    __table_args__ = (
        UniqueConstraint('classroom_id', 'curriculum_id', 'semester_id', name='uq_classroomid_curriculumid_semesterid'),
    )

    def __str__(self):
        return f'{str(self.classroom)}-{str(self.curriculum)}-{str(self.semester)}'


class ScoreType(Enumerate):
    FIFTEEN_MINUTE = 1
    ONE_PERIOD = 2
    EXAM = 3
    FIRST_TERM_AVERAGE = 1
    SECOND_TERM_AVERAGE = 2


class Score(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    score_number = Column(Float, CheckConstraint('score_number >= 0 AND score_number <= 10'), nullable=True)
    score_type = Column(Enum(ScoreType), nullable=False)
    student_info_id = Column(Integer, ForeignKey(StudentInfo.id, ondelete='CASCADE'), nullable=False)
    student_info = relationship(StudentInfo, backref="scores", lazy=True)
    transcript_id = Column(Integer, ForeignKey(Transcript.id, ondelete='RESTRICT'), nullable=False)
    transcript = relationship("Transcript", backref="scores", lazy=True)

    def __str__(self):
        return f'{str(self.student_info)}-{self.score_type.name}'


class ClassroomTransfer(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_classroom_change = Column(Boolean, nullable=False, default=False)
    transfer_date = Column(Date, nullable=False, default=date.today)
    classroom_id = Column(Integer, ForeignKey(Classroom.id, ondelete='RESTRICT'), nullable=False)
    classroom = relationship(Classroom, backref='classroom_transfers', lazy=True)
    student_info_id = Column(Integer, ForeignKey(StudentInfo.id, ondelete='CASCADE'), nullable=False)
    student_info = relationship(StudentInfo, backref='classroom_transfers', lazy=True)

    __table_args__ = (
        UniqueConstraint('student_info_id', 'classroom_id', 'transfer_date',
                         name='uq_studentinfoid_classroom_transferdate'),
    )

    def __str__(self):
        return f'{str(self.classroom)}-{str(self.student_info)}'


class Rule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(50), unique=True, nullable=False)
    min_value = Column(Integer)
    max_value = Column(Integer)
    rule_content = Column(String(500), unique=True, nullable=False)

    def __str__(self):
        return self.rule_name


@db.event.listens_for(ApplicationForm, 'after_update')
def create_student_info_on_accepted(mapper, connection, target):
    if target.status == ApplicationFormStatus.ACCEPTED and not hasattr(target, 'student_info'):
        hashed_password = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
        student_info = StudentInfo(
            name=target.name,
            gender=target.gender,
            phone=target.phone,
            address=target.address,
            email=target.email,
            birthday=target.birthday,
            status=True,
            user=User(
                username=target.email,
                password=hashed_password,
                role=Role.STUDENT
            ),
            application_form=target
        )
        db.session.add(student_info)
        connection.flush()


if __name__ == "__main__":
    with app.app_context():
        pass

# def upgrade():
#     op.execute("""
#     CREATE TRIGGER check_grade_delete
#     BEFORE DELETE ON grade
#     FOR EACH ROW
#     BEGIN
#         SIGNAL SQLSTATE '45000'
#         SET MESSAGE_TEXT = 'Can not delete. School year must has at least 3 grades.';
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
#         SELECT student_number INTO student_count
#         FROM classroom
#         WHERE id = NEW.classroom_id;
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
#
#         UPDATE classroom
#         SET student_number = student_number + 1
#         WHERE id = NEW.classroom_id;
#     END;
#     """)
#
#     op.execute("""
#     CREATE TRIGGER update_student_number_after_delete
#     AFTER DELETE ON classroom_transfer
#     FOR EACH ROW
#     BEGIN
#         UPDATE classroom
#         SET student_number = student_number - 1
#         WHERE id = OLD.classroom_id;
#     END;
#     """)
#
#     op.execute("""
#     CREATE TRIGGER check_semester_delete
#     BEFORE DELETE ON semester
#     FOR EACH ROW
#     BEGIN
#         SIGNAL SQLSTATE '45000'
#         SET MESSAGE_TEXT = 'Cannot delete semester: Not enough semesters for this school year.';
#     END;
#     """)
#
#     op.execute("""
#     CREATE TRIGGER check_min_classroom
#     BEFORE DELETE ON classroom
#     FOR EACH ROW
#     BEGIN
#         DECLARE class_count INT;
#
#         -- Đếm số lớp học còn lại trong khối
#         SELECT COUNT(*) INTO class_count
#         FROM classroom
#         WHERE grade_id = OLD.grade_id;
#
#         -- Nếu không còn lớp nào, báo lỗi
#         IF class_count <= 1 THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Grade must have at least 1 classroom.';
#         END IF;
#     END;
#     """)
#
#     op.execute("""
#     CREATE TRIGGER check_score_insert
#     BEFORE INSERT ON score
#     FOR EACH ROW
#     BEGIN
#         DECLARE score_count INT;
#
#         -- Kiểm tra điểm 15 phút
#         IF NEW.score_type = 'FIFTEEN_MINUTE' THEN
#             SELECT COUNT(*) INTO score_count
#             FROM score
#             WHERE student_info_id = NEW.student_info_id
#               AND transcript_id = NEW.transcript_id
#               AND score_type = 'FIFTEEN_MINUTE';
#
#             IF score_count >= 5 THEN
#                 SIGNAL SQLSTATE '45000'
#                 SET MESSAGE_TEXT = 'Student already has maximum fifteen-minute score number.';
#             END IF;
#         END IF;
#
#         -- Kiểm tra điểm 1 tiết
#         IF NEW.score_type = 'ONE_PERIOD' THEN
#             SELECT COUNT(*) INTO score_count
#             FROM score
#             WHERE student_info_id = NEW.student_info_id
#               AND transcript_id = NEW.transcript_id
#               AND score_type = 'ONE_PERIOD';
#
#             IF score_count >= 3 THEN
#                 SIGNAL SQLSTATE '45000'
#                 SET MESSAGE_TEXT = 'Student already has maximum one-period score number.';
#             END IF;
#         END IF;
#
#         -- Kiểm tra điểm thi
#         IF NEW.score_type = 'EXAM' THEN
#             SELECT COUNT(*) INTO score_count
#             FROM score
#             WHERE student_info_id = NEW.student_info_id
#               AND transcript_id = NEW.transcript_id
#               AND score_type = 'EXAM';
#
#             IF score_count >= 1 THEN
#                 SIGNAL SQLSTATE '45000'
#                 SET MESSAGE_TEXT = 'Student can only have 1 exam score.';
#             END IF;
#         END IF;
#
#     END;
#     """)
#
#     op.execute("""
#     CREATE TRIGGER check_score_delete
#     BEFORE DELETE ON score
#     FOR EACH ROW
#     BEGIN
#         DECLARE score_count INT;
#
#         -- Kiểm tra điểm 15 phút
#         IF OLD.score_type = 'FIFTEEN_MINUTE' THEN
#             SELECT COUNT(*) INTO score_count
#             FROM score
#             WHERE student_info_id = OLD.student_info_id
#               AND transcript_id = OLD.transcript_id
#               AND score_type = 'FIFTEEN_MINUTE';
#
#             IF score_count <= 1 THEN
#                 SIGNAL SQLSTATE '45000'
#                 SET MESSAGE_TEXT = 'Student cannot have less than 1 fifteen-minute score.';
#             END IF;
#         END IF;
#
#         -- Kiểm tra điểm 1 tiết
#         IF OLD.score_type = 'ONE_PERIOD' THEN
#             SELECT COUNT(*) INTO score_count
#             FROM score
#             WHERE student_info_id = OLD.student_info_id
#               AND transcript_id = OLD.transcript_id
#               AND score_type = 'ONE_PERIOD';
#
#             IF score_count <= 1 THEN
#                 SIGNAL SQLSTATE '45000'
#                 SET MESSAGE_TEXT = 'Cannot delete: Student has less than 1 one-period score left.';
#             END IF;
#         END IF;
#
#         -- Kiểm tra điểm thi
#         IF OLD.score_type = 'EXAM' THEN
#             SELECT COUNT(*) INTO score_count
#             FROM score
#             WHERE student_info_id = OLD.student_info_id
#               AND transcript_id = OLD.transcript_id
#               AND score_type = 'EXAM';
#
#             IF score_count <= 1 THEN
#                 SIGNAL SQLSTATE '45000'
#                 SET MESSAGE_TEXT = 'Student must have at least 1 exam score.';
#             END IF;
#         END IF;
#
#     END;
#     """)
#
#     op.execute("""
#     CREATE TRIGGER check_student_age
#     BEFORE INSERT ON student_info
#     FOR EACH ROW
#     BEGIN
#         DECLARE min_age INT;
#         DECLARE max_age INT;
#         DECLARE student_age INT;
#
#         -- Lấy giới hạn độ tuổi từ bảng Rule (id = 1)
#         SELECT min_value, max_value INTO min_age, max_age
#         FROM rule
#         WHERE id = 1;
#
#         -- Kiểm tra nếu không có quy định về độ tuổi, mặc định từ 0 đến 100
#         IF min_age IS NULL OR max_age IS NULL THEN
#             SET min_age = 15;
#             SET max_age = 20;
#         END IF;
#
#         -- Tính toán tuổi học sinh từ ngày sinh
#         SET student_age = TIMESTAMPDIFF(YEAR, NEW.birthday, CURDATE());
#
#         -- Kiểm tra xem tuổi học sinh có nằm trong giới hạn không
#         IF student_age < min_age OR student_age > max_age THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Student age is not appropriate.';
#         END IF;
#     END;
#     """)
#
#     op.execute("""
#         CREATE TRIGGER check_max_student_update
#         BEFORE UPDATE ON classroom_transfer
#         FOR EACH ROW
#         BEGIN
#             DECLARE student_count INT;
#             DECLARE max_count INT;
#             DECLARE old_classroom_id INT;
#
#             -- Lấy số lượng học sinh hiện tại trong lớp mới
#             SELECT student_number INTO student_count
#             FROM classroom
#             WHERE id = NEW.classroom_id;
#
#             -- Lấy giới hạn học sinh của lớp từ bảng Rule
#             SELECT max_value INTO max_count
#             FROM rule
#             WHERE id = 4;
#
#             -- Nếu không có giới hạn, mặc định là 40
#             IF max_count IS NULL THEN
#                 SET max_count = 40;
#             END IF;
#
#             -- Kiểm tra nếu lớp đã đủ số học sinh theo giới hạn
#             IF student_count >= max_count AND NEW.classroom_id != OLD.classroom_id THEN
#                 SIGNAL SQLSTATE '45000'
#                 SET MESSAGE_TEXT = 'Classroom reached max student number.';
#             END IF;
#
#             -- Giảm số lượng học sinh ở lớp cũ
#             IF NEW.classroom_id != OLD.classroom_id THEN
#                 UPDATE classroom
#                 SET student_number = student_number - 1
#                 WHERE id = OLD.classroom_id;
#             END IF;
#
#             -- Tăng số lượng học sinh ở lớp mới
#             IF NEW.classroom_id != OLD.classroom_id THEN
#                 UPDATE classroom
#                 SET student_number = student_number + 1
#                 WHERE id = NEW.classroom_id;
#             END IF;
#
#         END;
#         """)
#
#     op.execute("""
#         CREATE TRIGGER check_score_update
#         BEFORE UPDATE ON score
#         FOR EACH ROW
#         BEGIN
#             DECLARE score_count INT;
#
#             -- Kiểm tra điểm 15 phút
#             IF NEW.score_type = 'FIFTEEN_MINUTE' THEN
#                 SELECT COUNT(*) INTO score_count
#                 FROM score
#                 WHERE student_info_id = NEW.student_info_id
#                   AND transcript_id = NEW.transcript_id
#                   AND score_type = 'FIFTEEN_MINUTE';
#
#                 IF score_count > 5 THEN
#                     SIGNAL SQLSTATE '45000'
#                     SET MESSAGE_TEXT = 'Student already has maximum fifteen-minute score number.';
#                 END IF;
#             END IF;
#
#             -- Kiểm tra điểm 1 tiết
#             IF NEW.score_type = 'ONE_PERIOD' THEN
#                 SELECT COUNT(*) INTO score_count
#                 FROM score
#                 WHERE student_info_id = NEW.student_info_id
#                   AND transcript_id = NEW.transcript_id
#                   AND score_type = 'ONE_PERIOD';
#
#                 IF score_count > 3 THEN
#                     SIGNAL SQLSTATE '45000'
#                     SET MESSAGE_TEXT = 'Student already has maximum one-period score number.';
#                 END IF;
#             END IF;
#
#             -- Kiểm tra điểm thi
#             IF NEW.score_type = 'EXAM' THEN
#                 SELECT COUNT(*) INTO score_count
#                 FROM score
#                 WHERE student_info_id = NEW.student_info_id
#                   AND transcript_id = NEW.transcript_id
#                   AND score_type = 'EXAM';
#
#                 IF score_count > 1 THEN
#                     SIGNAL SQLSTATE '45000'
#                     SET MESSAGE_TEXT = 'Student can only have 1 exam score.';
#                 END IF;
#             END IF;
#
#         END;
#         """)
#
#     op.execute("""
#         CREATE TRIGGER check_student_age_update
#         BEFORE UPDATE ON student_info
#         FOR EACH ROW
#         BEGIN
#             DECLARE min_age INT;
#             DECLARE max_age INT;
#             DECLARE student_age INT;
#
#             -- Lấy giới hạn độ tuổi từ bảng Rule (id = 1)
#             SELECT min_value, max_value INTO min_age, max_age
#             FROM rule
#             WHERE id = 1;
#
#             -- Kiểm tra nếu không có quy định về độ tuổi, mặc định từ 15 đến 20
#             IF min_age IS NULL OR max_age IS NULL THEN
#                 SET min_age = 15;
#                 SET max_age = 20;
#             END IF;
#
#             -- Tính toán tuổi học sinh từ ngày sinh
#             SET student_age = TIMESTAMPDIFF(YEAR, NEW.birthday, CURDATE());
#
#             -- Kiểm tra xem tuổi học sinh có nằm trong giới hạn không
#             IF student_age < min_age OR student_age > max_age THEN
#                 SIGNAL SQLSTATE '45000'
#                 SET MESSAGE_TEXT = 'Student age is not appropriate.';
#             END IF;
#         END;
#         """)
#
#
# def downgrade():
#     op.execute("""DROP TRIGGER IF EXISTS check_grade_insert;""")
#     op.execute("""DROP TRIGGER IF EXISTS check_grade_delete;""")
#     op.execute("""DROP TRIGGER IF EXISTS check_max_student;""")
#     op.execute("""DROP TRIGGER IF EXISTS update_student_number_after_delete;""")
#     op.execute("""DROP TRIGGER IF EXISTS check_semester_delete;""")
#     op.execute("""DROP TRIGGER IF EXISTS check_min_classroom;""")
#     op.execute("""DROP TRIGGER IF EXISTS check_score_delete;""")
#     op.execute("""DROP TRIGGER IF EXISTS check_score_insert;""")
#     op.execute("""DROP TRIGGER IF EXISTS check_student_age;""")
#     op.execute("""DROP TRIGGER IF EXISTS check_max_student_update;""")
#     op.execute("""DROP TRIGGER IF EXISTS check_score_update;""")
#     op.execute("""DROP TRIGGER IF EXISTS check_student_age_update;""")
