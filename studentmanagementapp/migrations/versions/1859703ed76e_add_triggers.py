"""add triggers

Revision ID: 1859703ed76e
Revises: efea85c489e8
Create Date: 2024-12-22 00:01:11.397308

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1859703ed76e'
down_revision = 'efea85c489e8'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TRIGGER check_grade_delete
    BEFORE DELETE ON grade
    FOR EACH ROW
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Can not delete. School year must has at least 3 grades.';
    END;
    """)

    op.execute("""
    CREATE TRIGGER check_max_student
    BEFORE INSERT ON classroom_transfer
    FOR EACH ROW
    BEGIN
        DECLARE student_count INT;
        DECLARE max_count INT;

        -- Lấy số lượng học sinh hiện tại trong lớp
        SELECT student_number INTO student_count
        FROM classroom
        WHERE id = NEW.classroom_id;

        -- Lấy giới hạn học sinh của lớp từ bảng LopHoc
        SELECT max_value INTO max_count
        FROM rule
        WHERE id = 4;

        -- Nếu không có giới hạn, mặc định là 40
        IF max_count IS NULL THEN
            SET max_count = 40;
        END IF;

        -- Kiểm tra nếu lớp đã đủ số học sinh theo giới hạn
        IF student_count >= max_count THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Classroom reached max student number.';
        END IF;

        UPDATE classroom
        SET student_number = student_number + 1
        WHERE id = NEW.classroom_id;
    END;
    """)

    op.execute("""
    CREATE TRIGGER update_student_number_after_delete
    AFTER DELETE ON classroom_transfer
    FOR EACH ROW
    BEGIN
        UPDATE classroom
        SET student_number = student_number - 1
        WHERE id = OLD.classroom_id;
    END;
    """)

    op.execute("""
    CREATE TRIGGER check_semester_delete
    BEFORE DELETE ON semester
    FOR EACH ROW
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot delete semester: Not enough semesters for this school year.';
    END;
    """)

    op.execute("""
    CREATE TRIGGER check_min_classroom
    BEFORE DELETE ON classroom
    FOR EACH ROW
    BEGIN
        DECLARE class_count INT;

        -- Đếm số lớp học còn lại trong khối
        SELECT COUNT(*) INTO class_count
        FROM classroom
        WHERE grade_id = OLD.grade_id;

        -- Nếu không còn lớp nào, báo lỗi
        IF class_count <= 1 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Grade must have at least 1 classroom.';
        END IF;
    END;
    """)

    op.execute("""
    CREATE TRIGGER check_score_insert
    BEFORE INSERT ON score
    FOR EACH ROW
    BEGIN
        DECLARE score_count INT;

        -- Kiểm tra điểm 15 phút
        IF NEW.score_type = 'FIFTEEN_MINUTE' THEN
            SELECT COUNT(*) INTO score_count
            FROM score
            WHERE student_info_id = NEW.student_info_id
              AND transcript_id = NEW.transcript_id
              AND score_type = 'FIFTEEN_MINUTE';

            IF score_count >= 5 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Student already has maximum fifteen-minute score number.';
            END IF;
        END IF;

        -- Kiểm tra điểm 1 tiết
        IF NEW.score_type = 'ONE_PERIOD' THEN
            SELECT COUNT(*) INTO score_count
            FROM score
            WHERE student_info_id = NEW.student_info_id
              AND transcript_id = NEW.transcript_id
              AND score_type = 'ONE_PERIOD';

            IF score_count >= 3 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Student already has maximum one-period score number.';
            END IF;
        END IF;

        -- Kiểm tra điểm thi
        IF NEW.score_type = 'EXAM' THEN
            SELECT COUNT(*) INTO score_count
            FROM score
            WHERE student_info_id = NEW.student_info_id
              AND transcript_id = NEW.transcript_id
              AND score_type = 'EXAM';

            IF score_count >= 1 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Student can only have 1 exam score.';
            END IF;
        END IF;

    END;
    """)

    op.execute("""
    CREATE TRIGGER check_score_delete
    BEFORE DELETE ON score
    FOR EACH ROW
    BEGIN
        DECLARE score_count INT;

        -- Kiểm tra điểm 15 phút
        IF OLD.score_type = 'FIFTEEN_MINUTE' THEN
            SELECT COUNT(*) INTO score_count
            FROM score
            WHERE student_info_id = OLD.student_info_id
              AND transcript_id = OLD.transcript_id
              AND score_type = 'FIFTEEN_MINUTE';

            IF score_count <= 1 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Student cannot have less than 1 fifteen-minute score.';
            END IF;
        END IF;

        -- Kiểm tra điểm 1 tiết
        IF OLD.score_type = 'ONE_PERIOD' THEN
            SELECT COUNT(*) INTO score_count
            FROM score
            WHERE student_info_id = OLD.student_info_id
              AND transcript_id = OLD.transcript_id
              AND score_type = 'ONE_PERIOD';

            IF score_count <= 1 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Cannot delete: Student has less than 1 one-period score left.';
            END IF;
        END IF;

        -- Kiểm tra điểm thi
        IF OLD.score_type = 'EXAM' THEN
            SELECT COUNT(*) INTO score_count
            FROM score
            WHERE student_info_id = OLD.student_info_id
              AND transcript_id = OLD.transcript_id
              AND score_type = 'EXAM';

            IF score_count <= 1 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Student must have at least 1 exam score.';
            END IF;
        END IF;

    END;
    """)

    op.execute("""
    CREATE TRIGGER check_student_age
    BEFORE INSERT ON student_info
    FOR EACH ROW
    BEGIN
        DECLARE min_age INT;
        DECLARE max_age INT;
        DECLARE student_age INT;

        -- Lấy giới hạn độ tuổi từ bảng Rule (id = 1)
        SELECT min_value, max_value INTO min_age, max_age
        FROM rule
        WHERE id = 1;

        -- Kiểm tra nếu không có quy định về độ tuổi, mặc định từ 0 đến 100
        IF min_age IS NULL OR max_age IS NULL THEN
            SET min_age = 15;
            SET max_age = 20;
        END IF;

        -- Tính toán tuổi học sinh từ ngày sinh
        SET student_age = TIMESTAMPDIFF(YEAR, NEW.birthday, CURDATE());

        -- Kiểm tra xem tuổi học sinh có nằm trong giới hạn không
        IF student_age < min_age OR student_age > max_age THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Student age is not appropriate.';
        END IF;
    END;
    """)

    op.execute("""
        CREATE TRIGGER check_max_student_update
        BEFORE UPDATE ON classroom_transfer
        FOR EACH ROW
        BEGIN
            DECLARE student_count INT;
            DECLARE max_count INT;
            DECLARE old_classroom_id INT;

            -- Lấy số lượng học sinh hiện tại trong lớp mới
            SELECT student_number INTO student_count
            FROM classroom
            WHERE id = NEW.classroom_id;

            -- Lấy giới hạn học sinh của lớp từ bảng Rule
            SELECT max_value INTO max_count
            FROM rule
            WHERE id = 4;

            -- Nếu không có giới hạn, mặc định là 40
            IF max_count IS NULL THEN
                SET max_count = 40;
            END IF;

            -- Kiểm tra nếu lớp đã đủ số học sinh theo giới hạn
            IF student_count >= max_count AND NEW.classroom_id != OLD.classroom_id THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Classroom reached max student number.';
            END IF;

            -- Giảm số lượng học sinh ở lớp cũ
            IF NEW.classroom_id != OLD.classroom_id THEN
                UPDATE classroom
                SET student_number = student_number - 1
                WHERE id = OLD.classroom_id;
            END IF;

            -- Tăng số lượng học sinh ở lớp mới
            IF NEW.classroom_id != OLD.classroom_id THEN
                UPDATE classroom
                SET student_number = student_number + 1
                WHERE id = NEW.classroom_id;
            END IF;

        END;
        """)

    op.execute("""
        CREATE TRIGGER check_score_update
        BEFORE UPDATE ON score
        FOR EACH ROW
        BEGIN
            DECLARE score_count INT;

            -- Kiểm tra điểm 15 phút
            IF NEW.score_type = 'FIFTEEN_MINUTE' THEN
                SELECT COUNT(*) INTO score_count
                FROM score
                WHERE student_info_id = NEW.student_info_id
                  AND transcript_id = NEW.transcript_id
                  AND score_type = 'FIFTEEN_MINUTE';

                IF score_count > 5 THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Student already has maximum fifteen-minute score number.';
                END IF;
            END IF;

            -- Kiểm tra điểm 1 tiết
            IF NEW.score_type = 'ONE_PERIOD' THEN
                SELECT COUNT(*) INTO score_count
                FROM score
                WHERE student_info_id = NEW.student_info_id
                  AND transcript_id = NEW.transcript_id
                  AND score_type = 'ONE_PERIOD';

                IF score_count > 3 THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Student already has maximum one-period score number.';
                END IF;
            END IF;

            -- Kiểm tra điểm thi
            IF NEW.score_type = 'EXAM' THEN
                SELECT COUNT(*) INTO score_count
                FROM score
                WHERE student_info_id = NEW.student_info_id
                  AND transcript_id = NEW.transcript_id
                  AND score_type = 'EXAM';

                IF score_count > 1 THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Student can only have 1 exam score.';
                END IF;
            END IF;

        END;
        """)

    op.execute("""
        CREATE TRIGGER check_student_age_update
        BEFORE UPDATE ON student_info
        FOR EACH ROW
        BEGIN
            DECLARE min_age INT;
            DECLARE max_age INT;
            DECLARE student_age INT;

            -- Lấy giới hạn độ tuổi từ bảng Rule (id = 1)
            SELECT min_value, max_value INTO min_age, max_age
            FROM rule
            WHERE id = 1;

            -- Kiểm tra nếu không có quy định về độ tuổi, mặc định từ 15 đến 20
            IF min_age IS NULL OR max_age IS NULL THEN
                SET min_age = 15;
                SET max_age = 20;
            END IF;

            -- Tính toán tuổi học sinh từ ngày sinh
            SET student_age = TIMESTAMPDIFF(YEAR, NEW.birthday, CURDATE());

            -- Kiểm tra xem tuổi học sinh có nằm trong giới hạn không
            IF student_age < min_age OR student_age > max_age THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Student age is not appropriate.';
            END IF;
        END;
        """)


def downgrade():
    op.execute("""DROP TRIGGER IF EXISTS check_grade_insert;""")
    op.execute("""DROP TRIGGER IF EXISTS check_grade_delete;""")
    op.execute("""DROP TRIGGER IF EXISTS check_max_student;""")
    op.execute("""DROP TRIGGER IF EXISTS update_student_number_after_delete;""")
    op.execute("""DROP TRIGGER IF EXISTS check_semester_delete;""")
    op.execute("""DROP TRIGGER IF EXISTS check_min_classroom;""")
    op.execute("""DROP TRIGGER IF EXISTS check_score_delete;""")
    op.execute("""DROP TRIGGER IF EXISTS check_score_insert;""")
    op.execute("""DROP TRIGGER IF EXISTS check_student_age;""")
    op.execute("""DROP TRIGGER IF EXISTS check_max_student_update;""")
    op.execute("""DROP TRIGGER IF EXISTS check_score_update;""")
    op.execute("""DROP TRIGGER IF EXISTS check_student_age_update;""")
