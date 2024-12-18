"""Add Triggers

Revision ID: 531ef28718a2
Revises: 2b0649f4a574
Create Date: 2024-12-18 14:18:28.307325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '531ef28718a2'
down_revision = '2b0649f4a574'
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
        WHERE classroom_id = NEW.classroom_id;

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
    CREATE TRIGGER check_fifteen_minute_score_insert
    BEFORE INSERT ON fifteen_minute_score
    FOR EACH ROW
    BEGIN
        DECLARE fifteen_minute_scores_count INT;
        SELECT COUNT(*) INTO fifteen_minute_scores_count
        FROM fifteen_minute_score
        WHERE student_info_id = NEW.student_info_id
            AND transcript_id = NEW.transcript_id;

        IF fifteen_minute_scores_count >= 5 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Student already has maximum fifteen-minute score number.';
        END IF;
    END;
    """)

    op.execute("""
    CREATE TRIGGER check_fifteen_minute_score_delete
    BEFORE DELETE ON fifteen_minute_score
    FOR EACH ROW
    BEGIN
        DECLARE fifteen_minute_scores_count INT;

        -- Đếm số lượng điểm 15 phút của học sinh và bảng điểm tương ứng
        SELECT COUNT(*) INTO fifteen_minute_scores_count
        FROM fifteen_minute_score
        WHERE student_info_id = OLD.student_info_id
            AND transcript_id = OLD.transcript_id;

        -- Nếu số lượng điểm nhỏ hơn 1, không cho phép xóa
        IF fifteen_minute_scores_count <= 1 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Student can not have less than 1 fifteen-minute score.';
        END IF;
    END;
    """)

    op.execute("""
    CREATE TRIGGER check_one_period_score_delete
    BEFORE DELETE ON one_period_score
    FOR EACH ROW
    BEGIN
        DECLARE one_period_score_count INT;

        -- Đếm số lượng điểm một tiết của học sinh và bảng điểm tương ứng
        SELECT COUNT(*) INTO one_period_score_count
        FROM one_period_score
        WHERE student_info_id = OLD.student_info_id
            AND transcript_id = OLD.transcript_id;

        -- Nếu số lượng điểm nhỏ hơn 1, không cho phép xóa
        IF one_period_score_count <= 1 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot delete: Student has less than 1 one-period score left.';
        END IF;
    END;
    """)

    op.execute("""  
    CREATE TRIGGER check_one_period_score_insert
    BEFORE INSERT ON one_period_score
    FOR EACH ROW
    BEGIN
        DECLARE one_period_score_count INT;
        SELECT COUNT(*) INTO one_period_score_count
        FROM one_period_score
        WHERE student_info_id = NEW.student_info_id
            AND transcript_id = NEW.transcript_id;

        IF one_period_score_count >= 3 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Student already has maximum one period score number.';
        END IF;
    END;
    """)

    op.execute("""  
    CREATE TRIGGER check_exam_score_insert
    BEFORE INSERT ON exam_score
    FOR EACH ROW
    BEGIN
        DECLARE exam_score_count INT;
        SELECT COUNT(*) INTO exam_score_count
        FROM exam_score
        WHERE student_info_id = NEW.student_info_id
            AND transcript_id = NEW.transcript_id;

        IF exam_score_count >= 1 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Student must have at 1 exam score.';
        END IF;
    END;
    """)

    op.execute("""  
        CREATE TRIGGER check_exam_score_delete
        BEFORE DELETE ON exam_score
        FOR EACH ROW
        BEGIN
            DECLARE exam_score_count INT;
            SELECT COUNT(*) INTO exam_score_count
            FROM exam_score
            WHERE student_info_id = OLD.student_info_id
                AND transcript_id = OLD.transcript_id;

            IF exam_score_count <= 1 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Student must have at 1 exam score.';
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


def downgrade():
    op.execute("""
    DROP TRIGGER IF EXISTS check_grade_insert;
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS check_grade_delete;
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS check_max_student;
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS update_student_number_after_delete;
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS check_semester_delete;
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS check_min_classroom
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS check_fifteen_minute_score_insert
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS check_fifteen_minute_score_delete
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS check_one_period_score_insert
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS check_one_period_score_delete
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS check_exam_score_insert
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS check_exam_score_delete
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS check_student_age
    """)