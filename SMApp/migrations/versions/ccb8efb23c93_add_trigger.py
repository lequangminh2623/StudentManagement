"""Add trigger

Revision ID: ccb8efb23c93
Revises: 8705036a0f15
Create Date: 2024-12-08 16:40:52.470503

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ccb8efb23c93'
down_revision = '8705036a0f15'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TRIGGER kiem_tra_khoi_lop_insert
    BEFORE INSERT ON khoi_lop
    FOR EACH ROW
    BEGIN
        DECLARE count_khoi INT;

        -- Lấy số lượng khối lớp hiện tại của năm học
        SELECT COUNT(DISTINCT ten_khoi)
        INTO count_khoi
        FROM khoi_lop
        WHERE nam_hoc_id = NEW.nam_hoc_id;

        -- Kiểm tra nếu vượt quá 3 khối lớp
        IF count_khoi >= 3 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Không thể thêm. Năm học đã đủ 3 khối lớp.';
        END IF;
    END;
    """)

    op.execute("""
    CREATE TRIGGER kiem_tra_khoi_lop_delete
    BEFORE DELETE ON khoi_lop
    FOR EACH ROW
    BEGIN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Không thể xóa. Năm học phải có ít nhất 3 khối lớp.';
    END;
    """)

    op.execute("""
    CREATE TRIGGER kiem_tra_hoc_sinh_toi_da
    BEFORE INSERT ON chuyen_lop
    FOR EACH ROW
    BEGIN
        DECLARE student_count INT;
        DECLARE sl_lon_nhat INT;

        -- Lấy số lượng học sinh hiện tại trong lớp
        SELECT COUNT(*) INTO student_count
        FROM chuyen_lop
        WHERE lop_hoc_id = NEW.lop_hoc_id;

        -- Lấy giới hạn học sinh của lớp từ bảng LopHoc
        SELECT gioi_han_tren INTO sl_lon_nhat
        FROM quy_dinh
        WHERE id = 4;

        -- Nếu không có giới hạn, mặc định là 40
        IF sl_lon_nhat IS NULL THEN
            SET sl_lon_nhat = 40;
        END IF;

        -- Kiểm tra nếu lớp đã đủ số học sinh theo giới hạn
        IF student_count >= sl_lon_nhat THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Lớp học đã đạt giới hạn học sinh tối đa.';
        END IF;
    END;
    """)

    op.execute("""
    CREATE TRIGGER kiem_tra_hoc_ky
    BEFORE INSERT ON hoc_ky
    FOR EACH ROW
    BEGIN
        DECLARE hk_count INT;
        DECLARE hoc_ky_da_ton_tai INT;

        -- Đếm số học kỳ trong năm học hiện tại
        SELECT COUNT(*) INTO hk_count
        FROM hoc_ky
        WHERE nam_hoc_id = NEW.nam_hoc_id;

        -- Nếu năm học đã có 2 học kỳ, không cho phép thêm học kỳ thứ 3
        IF hk_count >= 2 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Năm học này đã có đủ 2 học kỳ (HK1 và HK2).';
        END IF;

        -- Kiểm tra xem cả hai học kỳ HK1 và HK2 đã có trong năm học chưa
        IF NEW.ten_hoc_ky = 'HK1' OR NEW.ten_hoc_ky = 'HK2' THEN
            SELECT COUNT(*) INTO hoc_ky_da_ton_tai
            FROM hoc_ky
            WHERE nam_hoc_id = NEW.nam_hoc_id
              AND (ten_hoc_ky = 'HK1' OR ten_hoc_ky = 'HK2');

            -- Nếu cả hai học kỳ HK1 và HK2 chưa tồn tại, cho phép thêm
            IF hoc_ky_da_ton_tai >= 2 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Năm học này đã có đủ 2 học kỳ (HK1 và HK2).';
            END IF;
        END IF;
    END;
    """)

    op.execute("""
    CREATE TRIGGER kiem_tra_lop_hoc_toi_thieu
    AFTER DELETE ON lop_hoc
    FOR EACH ROW
    BEGIN
        DECLARE lop_count INT;

        -- Đếm số lớp học còn lại trong khối
        SELECT COUNT(*) INTO lop_count
        FROM lop_hoc
        WHERE khoi_lop_id = OLD.khoi_lop_id;

        -- Nếu không còn lớp nào, báo lỗi
        IF lop_count < 1 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Mỗi khối phải có ít nhất một lớp.';
        END IF;
    END;
    """)


    op.execute("""  
    CREATE TRIGGER kiem_tra_diem15p
    BEFORE INSERT ON diem15p
    FOR EACH ROW
    BEGIN
        DECLARE diem15p_count INT;
        SELECT COUNT(*) INTO diem15p_count
        FROM diem15p
        WHERE hoc_sinh_id = NEW.hoc_sinh_id
            AND bang_diem_id = NEW.bang_diem_id;
    
        IF diem15p_count >= 5 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Tối đa 5 cột điểm 15 phút cho mỗi học sinh trong chương trình học.';
        END IF;
    
        IF diem15p_count < 1 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Tối thiểu 1 cột điểm 15 phút cho mỗi học sinh trong chương trình học.';
        END IF;
    END;
    """)

    op.execute("""  
    CREATE TRIGGER kiem_tra_diem1tiet
    BEFORE INSERT ON diem1_tiet
    FOR EACH ROW
    BEGIN
        DECLARE diem1tiet_count INT;
        SELECT COUNT(*) INTO diem1tiet_count
        FROM diem1_tiet
        WHERE hoc_sinh_id = NEW.hoc_sinh_id
            AND bang_diem_id = NEW.bang_diem_id;

        IF diem1tiet_count >= 3 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Tối đa 3 cột điểm 1 tiết cho mỗi học sinh trong chương trình học.';
        END IF;

        IF diem15p_count < 1 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Tối thiểu 1 cột điểm 1 tiết cho mỗi học sinh trong chương trình học.';
        END IF;
    END;
    """)

    op.execute("""  
    CREATE TRIGGER kiem_tra_diemthi
    BEFORE INSERT ON diem_thi
    FOR EACH ROW
    BEGIN
        DECLARE diemthi_count INT;
        SELECT COUNT(*) INTO diemthi_count
        FROM diem_thi
        WHERE hoc_sinh_id = NEW.hoc_sinh_id
            AND bang_diem_id = NEW.bang_diem_id;

        IF diemthi_count != 1 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Phải có 1 cột điểm thi cho mỗi học sinh trong chương trình học.';
        END IF;
    END;
    """)


def downgrade():
    op.execute("""
    DROP TRIGGER IF EXISTS kiem_tra_khoi_lop_insert;
    """)

    op.execute("""
        DROP TRIGGER IF EXISTS kiem_tra_khoi_lop_delete;
        """)

    op.execute("""
    DROP TRIGGER IF EXISTS kiem_tra_hoc_sinh_toi_da
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS kiem_tra_tuoi_hoc_sinh
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS kiem_tra_lop_hoc_toi_thieu
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS kiem_tra_hoc_ky
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS kiem_tra_diem15p
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS kiem_tra_diem1tiet
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS kiem_tra_diemthi
    """)
