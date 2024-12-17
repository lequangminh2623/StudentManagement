from faker import Faker
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Boolean, Enum, Date, UniqueConstraint, \
    CheckConstraint, create_engine, text
from sqlalchemy.event import listens_for
from sqlalchemy.orm import relationship, declared_attr
from __init__ import db, app, migrate
from enum import Enum as Enumerate
from flask_login import UserMixin
from datetime import date
from sqlalchemy import event




engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])


class LoaiTaiKhoan(Enumerate):
    NGUOIQUANTRI = 1
    NHANVIEN = 2
    GIAOVIEN = 3
    HOCSINH = 4


class TaiKhoan(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_dang_nhap = Column(String(50), unique=True, nullable=False)
    mat_khau = Column(String(100), nullable=False)
    anh_dai_dien = Column(String(100),
                    default='https://res.cloudinary.com/dqw4mc8dg/image/upload/w_1000,c_fill,ar_1:1,g_auto,r_max,bo_5px_solid_red,b_rgb:262c35/v1733391370/aj6sc6isvelwkotlo1vw.png')
    loai_tai_khoan = Column(Enum(LoaiTaiKhoan), default=LoaiTaiKhoan.HOCSINH)
    nguoi_quan_tri = relationship("NguoiQuanTri", back_populates="tai_khoan", lazy=True)
    nhan_vien = relationship("NhanVien", back_populates="tai_khoan", lazy=True)
    giao_vien = relationship("GiaoVien", back_populates="tai_khoan", lazy=True)
    hoc_sinh = relationship("HocSinh", back_populates="tai_khoan", lazy=True)

    def __str__(self):
        return self.ten_dang_nhap


class NguoiDung(db.Model):
    __abstract__ = True

    @declared_attr
    def ho_ten(cls):
        return Column(String(50), nullable=False)

    @declared_attr
    def gioi_tinh(cls):
        return Column(Boolean, nullable=False)

    @declared_attr
    def sdt(cls):
        return Column(String(10), unique=True, nullable=False)

    @declared_attr
    def dia_chi(cls):
        return Column(String(100), nullable=False)

    @declared_attr
    def email(cls):
        return Column(String(50), unique=True, nullable=False)

    @declared_attr
    def ngay_sinh(cls):
        return Column(Date, nullable=False)

    @declared_attr
    def trang_thai(cls):
        return Column(Boolean, nullable=False)

    @declared_attr
    def tai_khoan_id(cls):
        return Column(Integer, ForeignKey(TaiKhoan.id, ondelete='SET NULL'), unique=True)

    @declared_attr
    def tai_khoan(cls):
        return relationship(TaiKhoan, back_populates='nguoi_quan_tri', lazy=True)

    def __str__(self):
        return self.ho_ten


class NguoiQuanTri(NguoiDung):
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Thiết lập back_populates với lớp TaiKhoan
    tai_khoan = relationship(TaiKhoan, back_populates="nguoi_quan_tri", lazy=True)


class NhanVien(NguoiDung):
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Thiết lập back_populates với lớp TaiKhoan
    tai_khoan = relationship(TaiKhoan, back_populates="nhan_vien", lazy=True)


class GiaoVien(NguoiDung):
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Thiết lập back_populates với lớp TaiKhoan
    tai_khoan = relationship(TaiKhoan, back_populates="giao_vien", lazy=True)


class NamHoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_nam_hoc = Column(String(50), unique=True, nullable=False)


class LoaiHocKy(Enumerate):
    HK1 = 'Học kỳ 1'
    HK2 = 'Học kỳ 2'


class HocKy(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_hoc_ky = Column(Enum(LoaiHocKy), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey(NamHoc.id, ondelete='RESTRICT'), nullable=False)
    nam_hoc = relationship(NamHoc, backref='ds_hoc_ky', lazy=True)

    __table_args__ = (
        UniqueConstraint('ten_hoc_ky', 'nam_hoc_id', name='uq_tenhocky_namhoc'),
    )

    def __str__(self):
        return self.ten_hoc_ky


class LoaiKhoiLop(Enumerate):
    KHOI_10 = 'Khối 10'
    KHOI_11 = 'Khối 11'
    KHOI_12 = 'Khối 12'


class KhoiLop(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_khoi = Column(Enum(LoaiKhoiLop), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey(NamHoc.id, ondelete='RESTRICT'), nullable=False)
    nam_hoc = relationship(NamHoc, backref='ds_khoi_lop', lazy=True)

    __table_args__ = (
        UniqueConstraint('ten_khoi', 'nam_hoc_id', name='uq_tenkhoi_namhoc'),
    )

    def __str__(self):
        return self.ten_khoi


class LopHoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_lop = Column(String(50), nullable=False)
    si_so = Column(Integer, nullable=False)
    khoi_lop_id = Column(ForeignKey(KhoiLop.id, ondelete='RESTRICT'), nullable=False)
    khoi_lop = relationship(KhoiLop, backref='ds_lop_hoc', lazy=True)

    __table_args__ = (
        UniqueConstraint('ten_lop', 'khoi_lop_id', name='uq_tenlop_khoilop'),
    )

    def __str__(self):
        return self.ten_lop


class TrangThaiHSXT(Enumerate):
    CHOXETTUYEN = 1
    DATRUNGTUYEN = 2
    KHONGTRUNGTUYEN = 3


class HoSoXetTuyen(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ho_ten = Column(String(50), nullable=False)
    gioi_tinh = Column(Boolean, nullable=False)
    sdt = Column(String(10), unique=True, nullable=False)
    dia_chi = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    ngay_sinh = Column(Date, nullable=False)
    trang_thai = Column(Enum(TrangThaiHSXT), default=TrangThaiHSXT.CHOXETTUYEN, nullable=False)

    def __str__(self):
        return self.ho_ten


class HocSinh(NguoiDung):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ho_so_xet_tuyen_id = Column(Integer, ForeignKey(HoSoXetTuyen.id, ondelete='SET NULL'), unique=True)
    ho_so_xet_tuyen = relationship(HoSoXetTuyen, backref='hoc_sinh', lazy=True)
    tai_khoan = relationship("TaiKhoan", back_populates="hoc_sinh", lazy=True)


class MonHoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_mon_hoc = Column(String(50), nullable=False, unique=True)

    def __str__(self):
        return self.ten_mon_hoc


class ChuongTrinhHoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_chuong_trinh = Column(String(50), nullable=False)
    khoi_lop_id = Column(Integer, ForeignKey(KhoiLop.id, ondelete='CASCADE'), nullable=False)
    khoi_lop = relationship(KhoiLop, backref='ds_chuong_trinh_hoc', lazy=True)
    mon_hoc_id = Column(Integer, ForeignKey(MonHoc.id, ondelete='CASCADE'), nullable=False)
    mon_hoc = relationship(MonHoc, backref='ds_chuong_trinh_hoc', lazy=True)

    __table_args__ = (
        UniqueConstraint('khoi_lop_id', 'mon_hoc_id', name='uq_khoilop_monhoc'),
    )

    def __str__(self):
        return self.ten_chuong_trinh


class BaoCao(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_bao_cao = Column(String(50), nullable=False)
    mon_hoc_id = Column(Integer, ForeignKey(MonHoc.id, ondelete='CASCADE'), nullable=False)
    mon_hoc = relationship(MonHoc, backref='ds_bao_cao', lazy=True)
    hoc_ky_id = Column(Integer, ForeignKey(HocKy.id, ondelete='CASCADE'), nullable=False)
    hoc_ky = relationship(HocKy, backref='ds_bao_cao', lazy=True)

    __table_args__ = (
        UniqueConstraint('mon_hoc_id', 'hoc_ky_id', name='uq_tenkhoi_namhoc'),
    )

    def __str__(self):
        return self.ten_bao_cao


class ThongKe(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    so_luong_dat = Column(Integer, nullable=False)
    ti_le = Column(Float, nullable=False)
    lop_hoc_id = Column(Integer, ForeignKey(LopHoc.id, ondelete='CASCADE'), nullable=False)
    lop_hoc = relationship(LopHoc, backref='ds_thong_ke', lazy=True)
    bao_cao_id = Column(Integer, ForeignKey(BaoCao.id, ondelete='CASCADE'), nullable=False)
    bao_cao = relationship(BaoCao, backref='ds_thong_ke', lazy=False)

    __table_args__ = (
        UniqueConstraint('lop_hoc_id', 'bao_cao_id', name='uq_lophoc_baocao'),
    )

    def __str__(self):
        return self.lop_hoc


class BangDiem(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_bang_diem = Column(String(50), nullable=False)
    hoan_thanh = Column(Boolean, nullable=False, default=False)
    lop_hoc_id = Column(Integer, ForeignKey(LopHoc.id, ondelete='CASCADE'), nullable=False)
    lop_hoc = relationship(LopHoc, backref='ds_bang_diem', lazy=True)
    chuong_trinh_hoc_id = Column(Integer, ForeignKey(ChuongTrinhHoc.id, ondelete='RESTRICT'), nullable=False)
    chuong_trinh_hoc = relationship(ChuongTrinhHoc, backref='ds_bang_diem', lazy=True)
    hoc_ky_id = Column(Integer, ForeignKey(HocKy.id, ondelete='RESTRICT'), nullable=False)
    hoc_ky = relationship(HocKy, backref='ds_bang_diem', lazy=True)
    giao_vien_id = Column(Integer, ForeignKey(GiaoVien.id, ondelete='RESTRICT'), nullable=False)
    giao_vien = relationship(GiaoVien, backref='ds_bang_diem', lazy=True)

    ds_diem15p = relationship("Diem15p", back_populates="bang_diem", lazy=True)
    ds_diem1tiet = relationship("Diem1Tiet", back_populates="bang_diem", lazy=True)
    ds_diemthi = relationship("DiemThi", back_populates="bang_diem", lazy=True)
    ds_diemtbhk1 = relationship("DiemTBHK1", back_populates="bang_diem", lazy=True)
    ds_diemtbhk2 = relationship("DiemTBHK2", back_populates="bang_diem", lazy=True)

    __table_args__ = (
        UniqueConstraint('lop_hoc_id', 'chuong_trinh_hoc_id', 'hoc_ky_id', name='uq_tenkhoi_namhoc_hocky'),
    )

    def __str__(self):
        return self.ten_bang_diem


class CotDiem(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    so_diem = Column(Float, CheckConstraint('so_diem >= 0 AND so_diem <= 10'), nullable=True)
    he_so = Column(Integer, nullable=False)
    ten_cot = Column(String(50), nullable=False)
    bang_diem_id = Column(Integer, ForeignKey(BangDiem.id, ondelete='RESTRICT'), nullable=False)

    @declared_attr
    def bang_diem(cls):
        return relationship(BangDiem, back_populates=f"ds_{cls.__name__.lower()}", lazy=False)

    def __str__(self):
        return self.ten_cot


class Diem15p(CotDiem):
    he_so = 1
    ten = "Điểm 15 Phút"
    hoc_sinh_id = Column(Integer, ForeignKey(HocSinh.id, ondelete='CASCADE'), nullable=False)
    hoc_sinh = relationship(HocSinh, backref="ds_diem_15p", lazy=True)


class Diem1Tiet(CotDiem):
    he_so = 2
    ten = "Điểm 1 Tiết"
    hoc_sinh_id = Column(Integer, ForeignKey(HocSinh.id, ondelete='CASCADE'), nullable=False)
    hoc_sinh = relationship(HocSinh, backref="ds_diem_1tiet", lazy=True)


class DiemThi(CotDiem):
    he_so = 3
    ten = "Điểm Thi"
    hoc_sinh_id = Column(Integer, ForeignKey(HocSinh.id, ondelete='CASCADE'), nullable=False)
    hoc_sinh = relationship(HocSinh, backref="ds_diem_thi", lazy=True)


class DiemTBHK1(CotDiem):
    he_so = 1
    ten = "Điểm TB HK1"
    hoc_sinh_id = Column(Integer, ForeignKey(HocSinh.id, ondelete='CASCADE'), nullable=False)
    hoc_sinh = relationship(HocSinh, backref="ds_diem_tbhk1", lazy=True)


class DiemTBHK2(CotDiem):
    he_so = 2
    ten = "Điểm TB HK2"
    hoc_sinh_id = Column(Integer, ForeignKey(HocSinh.id, ondelete='CASCADE'), nullable=False)
    hoc_sinh = relationship(HocSinh, backref="ds_diem_tbhk2", lazy=True)


class ChuyenLop(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    la_doi_lop = Column(Boolean, nullable=False, default=False)
    ngay_chuyen = Column(Date, nullable=False, default=date.today)
    lop_hoc_id = Column(Integer, ForeignKey(LopHoc.id, ondelete='RESTRICT'), nullable=False)
    lop_hoc = relationship(LopHoc, backref='ds_chuyen_lop', lazy=True)
    hoc_sinh_id = Column(Integer, ForeignKey(HocSinh.id, ondelete='CASCADE'), nullable=False)
    hoc_sinh = relationship(HocSinh, backref='ds_chuyen_lop', lazy=True)

    __table_args__ = (
        UniqueConstraint('hoc_sinh_id', 'lop_hoc_id', 'ngay_chuyen', name='uq_hocsinh_lophoc_ngaychuyen'),
    )


class QuyDinh(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_quy_dinh = Column(String(50), unique=True, nullable=False)
    gioi_han_duoi = Column(Integer)
    gioi_han_tren = Column(Integer)
    noi_dung = Column(String(500), unique=True, nullable=False)

    def __str__(self):
        return self.ten


# @listens_for(KhoiLop.__table__, 'after_create')
# def kiem_tra_khoi_lop_trigger(target, connection, **kw):
#     trigger_sql = """
#     CREATE TRIGGER kiem_tra_khoi_lop
#     BEFORE INSERT OR DELETE ON khoi_lop
#     FOR EACH ROW
#     BEGIN
#         DECLARE count_khoi INT;
#         DECLARE khoi_da_ton_tai SET('KHOI_10', 'KHOI_11', 'KHOI_12');
#         DECLARE kiem_tra_khoi BOOLEAN;
#
#         -- Lấy số lượng khối lớp hiện tại của năm học
#         SELECT COUNT(DISTINCT ten_khoi)
#         INTO count_khoi
#         FROM khoi_lop
#         WHERE nam_hoc_id = IFNULL(NEW.nam_hoc_id, OLD.nam_hoc_id);
#
#         -- Lấy danh sách các khối lớp hiện tại
#         SELECT GROUP_CONCAT(DISTINCT ten_khoi)
#         INTO khoi_da_ton_tai
#         FROM khoi_lop
#         WHERE nam_hoc_id = IFNULL(NEW.nam_hoc_id, OLD.nam_hoc_id);
#
#         -- Kiểm tra nếu thêm mới
#         IF INSERTING THEN
#             IF count_khoi >= 3 THEN
#                 SIGNAL SQLSTATE '45000'
#                 SET MESSAGE_TEXT = 'Không thể thêm. Năm học đã đủ 3 khối lớp.';
#             END IF;
#         END IF;
#
#         -- Kiểm tra nếu xóa
#         IF DELETING THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Không thể xóa. Năm học phải có ít nhất 3 khối lớp.';
#         END IF;
#     END;
#     """
#     with engine.connect() as connection:
#         try:
#             connection.execute(text(trigger_sql))
#             print("Trigger created successfully.")
#         except Exception as e:
#             print(f"Error creating trigger: {e}")


# @listens_for(HocSinh.__table__, 'after_create')
# def kiem_tra_hoc_sinh_toi_da_trigger(target, connection, **kw):
#     trigger_sql = """
#     CREATE TRIGGER kiem_tra_hoc_sinh_toi_da
#     BEFORE INSERT ON chuyen_lop
#     FOR EACH ROW
#     BEGIN
#         DECLARE student_count INT;
#         DECLARE sl_lon_nhat INT;
#
#         -- Lấy số lượng học sinh hiện tại trong lớp
#         SELECT COUNT(*) INTO student_count
#         FROM chuyen_lop
#         WHERE lop_hoc_id = NEW.lop_hoc_id;
#
#         -- Lấy giới hạn học sinh của lớp từ bảng LopHoc
#         SELECT gioi_han_tren INTO sl_lon_nhat
#         FROM quy_dinh
#         WHERE id = 4;
#
#         -- Nếu không có giới hạn, mặc định là 40
#         IF sl_lon_nhat IS NULL THEN
#             SET sl_lon_nhat = 40;
#         END IF;
#
#         -- Kiểm tra nếu lớp đã đủ số học sinh theo giới hạn
#         IF student_count >= sl_lon_nhat THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Lớp học đã đạt giới hạn học sinh tối đa.';
#         END IF;
#     END;
#     """
#     with engine.connect() as connection:
#         try:
#             connection.execute(text(trigger_sql))
#             print("Trigger created successfully.")
#         except Exception as e:
#             print(f"Error creating trigger: {e}")


# @event.listens_for(HocSinh.__table__, 'after_create')
# def kiem_tra_tuoi_hoc_sinh_trigger(target, connection, **kw):
#     trigger_sql = """
#     CREATE TRIGGER kiem_tra_tuoi_hoc_sinh
#     BEFORE INSERT ON hoc_sinh
#     FOR EACH ROW
#     BEGIN
#         DECLARE tuoi_nho_nhat INT;
#         DECLARE tuoi_lon_nhat INT;
#         DECLARE tuoi_hoc_sinh INT;
#
#         -- Lấy giới hạn độ tuổi từ bảng QuyDinh (id = 1)
#         SELECT gioi_han_duoi, gioi_han_tren INTO tuoi_nho_nhat, tuoi_lon_nhat
#         FROM quy_dinh
#         WHERE id = 1;
#
#         -- Kiểm tra nếu không có quy định về độ tuổi, mặc định từ 0 đến 100
#         IF tuoi_nho_nhat IS NULL OR tuoi_lon_nhat IS NULL THEN
#             SET tuoi_nho_nhat = 15;
#             SET tuoi_lon_nhat = 20;
#         END IF;
#
#         -- Tính toán tuổi học sinh từ ngày sinh
#         SET tuoi_hoc_sinh = TIMESTAMPDIFF(YEAR, NEW.ngay_sinh, CURDATE());
#
#         -- Kiểm tra xem tuổi học sinh có nằm trong giới hạn không
#         IF tuoi_hoc_sinh < tuoi_nho_nhat OR tuoi_hoc_sinh > tuoi_lon_nhat THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Tuổi học sinh không hợp lệ, phải trong khoảng từ '
#                                || tuoi_nho_nhat || ' đến ' || tuoi_lon_nhat || ' tuổi.';
#         END IF;
#     END;
#     """
#     with engine.connect() as connection:
#         try:
#             connection.execute(text(trigger_sql))
#             print("Trigger created successfully.")
#         except Exception as e:
#             print(f"Error creating trigger: {e}")


# @listens_for(LopHoc.__table__, 'after_create')
# def kiem_tra_lop_hoc_toi_thieu_trigger(target, connection, **kw):
#     trigger_sql = """
#     CREATE TRIGGER kiem_tra_lop_hoc_toi_thieu
#     AFTER DELETE ON lop_hoc
#     FOR EACH ROW
#     BEGIN
#         DECLARE lop_count INT;
#
#         -- Đếm số lớp học còn lại trong khối
#         SELECT COUNT(*) INTO lop_count
#         FROM lop_hoc
#         WHERE khoi_lop_id = OLD.khoi_lop_id;
#
#         -- Nếu không còn lớp nào, báo lỗi
#         IF lop_count < 1 THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Mỗi khối phải có ít nhất một lớp.';
#         END IF;
#     END;
#     """
#     with engine.connect() as connection:
#         try:
#             connection.execute(text(trigger_sql))
#             print("Trigger created successfully.")
#         except Exception as e:
#             print(f"Error creating trigger: {e}")


# @event.listens_for(HocKy.__table__, 'after_create')
# def kiem_tra_hoc_ky_trigger(target, connection, **kw):
#     trigger_sql = """
#     CREATE TRIGGER kiem_tra_hoc_ky
#     BEFORE INSERT ON hoc_ky
#     FOR EACH ROW
#     BEGIN
#         DECLARE hk_count INT;
#
#         -- Đếm số học kỳ trong năm học hiện tại
#         SELECT COUNT(*) INTO hk_count
#         FROM hoc_ky
#         WHERE nam_hoc_id = NEW.nam_hoc_id;
#
#         -- Nếu năm học đã có 2 học kỳ, không cho phép thêm học kỳ thứ 3
#         IF hk_count >= 2 THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Năm học này đã có đủ 2 học kỳ (HK1 và HK2).';
#         END IF;
#
#         -- Kiểm tra xem cả hai học kỳ HK1 và HK2 đã có trong năm học chưa
#         IF NEW.ten_hoc_ky = 'HK1' OR NEW.ten_hoc_ky = 'HK2' THEN
#             DECLARE hoc_ky_da_ton_tai INT;
#             SELECT COUNT(*) INTO hoc_ky_da_ton_tai
#             FROM hoc_ky
#             WHERE nam_hoc_id = NEW.nam_hoc_id
#               AND (ten_hoc_ky = 'HK1' OR ten_hoc_ky = 'HK2');
#
#             -- Nếu cả hai học kỳ HK1 và HK2 chưa tồn tại, cho phép thêm
#             IF hoc_ky_da_ton_tai < 2 THEN
#                 -- Allow insertion
#             ELSE
#                 SIGNAL SQLSTATE '45000'
#                 SET MESSAGE_TEXT = 'Năm học này đã có đủ 2 học kỳ (HK1 và HK2).';
#             END IF;
#         END IF;
#     END;
#     """
#     with engine.connect() as connection:
#         try:
#             connection.execute(text(trigger_sql))
#             print("Trigger created successfully.")
#         except Exception as e:
#             print(f"Error creating trigger: {e}")


# @event.listens_for(Diem15p.__table__, 'after_create')
# def kiem_tra_diem15p_trigger(target, connection, **kw):
#     trigger_sql = """
#     CREATE TRIGGER kiem_tra_diem15p
#     BEFORE INSERT ON diem15p
#     FOR EACH ROW
#     BEGIN
#         DECLARE diem15p_count INT;
#         SELECT COUNT(*) INTO diem15p_count
#         FROM diem15p
#         WHERE hoc_sinh_id = NEW.hoc_sinh_id
#             AND bang_diem_id = NEW.bang_diem_id;
#
#         IF diem15p_count >= 5 THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Tối đa 5 cột điểm 15 phút cho mỗi học sinh trong chương trình học.';
#         END IF;
#
#         IF diem15p_count < 1 THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Tối thiểu 1 cột điểm 15 phút cho mỗi học sinh trong chương trình học.';
#         END IF;
#     END;
#     """
#     with engine.connect() as connection:
#         try:
#             connection.execute(text(trigger_sql))
#             print("Trigger created successfully.")
#         except Exception as e:
#             print(f"Error creating trigger: {e}")


# @event.listens_for(Diem1Tiet.__table__, 'after_create')
# def kiem_tra_diem1tiet_trigger(target, connection, **kw):
#     trigger_sql = """
#     CREATE TRIGGER kiem_tra_diem1tiet
#     BEFORE INSERT ON diem1_tiet
#     FOR EACH ROW
#     BEGIN
#         DECLARE diem1tiet_count INT;
#         SELECT COUNT(*) INTO diem1tiet_count
#         FROM diem1_tiet
#         WHERE hoc_sinh_id = NEW.hoc_sinh_id
#             AND bang_diem_id = NEW.bang_diem_id;
#
#         IF diem1tiet_count >= 3 THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Tối đa 3 cột điểm 1 tiết cho mỗi học sinh trong chương trình học.';
#         END IF;
#
#         IF diem15p_count < 1 THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Tối thiểu 1 cột điểm 1 tiết cho mỗi học sinh trong chương trình học.';
#         END IF;
#     END;
#     """
#     with engine.connect() as connection:
#         try:
#             connection.execute(text(trigger_sql))
#             print("Trigger created successfully.")
#         except Exception as e:
#             print(f"Error creating trigger: {e}")


# @event.listens_for(DiemThi.__table__, 'after_create')
# def kiem_tra_diemthi_trigger(target, connection, **kw):
#     trigger_sql = """
#     CREATE TRIGGER kiem_tra_diemthi
#     BEFORE INSERT ON diem_thi
#     FOR EACH ROW
#     BEGIN
#         DECLARE diemthi_count INT;
#         SELECT COUNT(*) INTO diemthi_count
#         FROM diem_thi
#         WHERE hoc_sinh_id = NEW.hoc_sinh_id
#             AND bang_diem_id = NEW.bang_diem_id;
#
#         IF diemthi_count != 1 THEN
#             SIGNAL SQLSTATE '45000'
#             SET MESSAGE_TEXT = 'Phải có 1 cột điểm thi cho mỗi học sinh trong chương trình học.';
#         END IF;
#     END;
#     """
#     with engine.connect() as connection:
#         try:
#             connection.execute(text(trigger_sql))
#             print("Trigger created successfully.")
#         except Exception as e:
#             print(f"Error creating trigger: {e}")




if __name__ == '__main__':
    with app.app_context():
        pass
