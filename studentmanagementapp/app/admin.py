from io import BytesIO

import PyPDF2
import openpyxl
from PyPDF2 import PdfMerger

from app import db, app, dao
from app.dao import get_summary_report, get_subjects, get_semesters, get_school_years
from app.models import Classroom, Grade, ApplicationForm, Curriculum, \
    Subject, StudentInfo, Rule, ApplicationFormStatus, Score, Role, User, Semester, SchoolYear
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask_admin import Admin, BaseView, expose
from flask import redirect, url_for, flash, request, Response, render_template, make_response

from reportlab.pdfgen import canvas

admin = Admin(app, name='StudentManagement', template_mode='bootstrap4')

class BaseAdminView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role.__eq__(Role.ADMIN)
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')


class ApplicationView(ModelView):
    column_list = ['name', 'gender', 'phone', 'address', 'email', 'birthday', 'status']
    column_filters = ['status', 'birthday']
    column_searchable_list = ['name']
    column_default_sort = ('status', True)


class RuleView(BaseAdminView):
    column_list = ['id', 'rule_name', 'rule_content']

    def update_model(self, form, model):
        if model.id not in [1, 4]:
            flash("Admin is only allowed to edit rules with IDs 1 and 4.", "error")
            return False
        try:
            return super(RuleView, self).update_model(form, model)
        except Exception as ex:
            flash('Failed to update record. {}'.format(ex), 'error')
            db.session.rollback()
            return False


class CurriculumView(BaseAdminView):
    column_list = ['subject', 'grade', 'grade.school_year']
    column_labels = {'grade.school_year': 'School Year'}


class StudentInfoView(BaseAdminView):
    column_list = ['name']


class ClassroomView(BaseAdminView):
    column_list = ['id', 'classroom_name', 'student_number', 'grade']
    column_filters = ['grade']
    column_searchable_list = ['classroom_name']


class SubjectView(BaseAdminView):
    column_list = ['subject_name', '']

class AuthenticatedView(BaseView):
        def is_accessible(self):
            return current_user.is_authenticated


class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

class PhoDiem(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        semesters = Semester.query.join(SchoolYear).all()
        subjects = Subject.query.all()

        stats = []
        selected_semester_id = None  # Học kỳ được chọn
        selected_subject_id = None  # Môn học được chọn
        selected_subject_name = ""  # Tên môn học được chọn

        if request.method == 'POST':
            selected_semester_id = request.form.get('semester_id')
            selected_subject_id = request.form.get('subject_id')

            # Filter scores based on the selected semester and subject
            stats = dao.diem_stats(semester_id=selected_semester_id, subject_id=selected_subject_id)

            # Lấy tên môn học được chọn
            if selected_subject_id:
                subject = Subject.query.get(selected_subject_id)
                if subject:
                    selected_subject_name = subject.subject_name

        return self.render('admin/phodiem.html',
                           stats=stats,
                           semesters=semesters,
                           subjects=subjects,
                           selected_semester_id=selected_semester_id,
                           selected_subject_id=selected_subject_id,
                           selected_subject_name=selected_subject_name)


    @expose('/export-excel', methods=['POST'])
    def export_excel(self):
        semester_id = request.form.get('semester_id')
        subject_id = request.form.get('subject_id')

        # Lấy thông tin học kỳ và môn học từ database
        semester = Semester.query.get(semester_id)
        subject = Subject.query.get(subject_id)

        # Lấy dữ liệu điểm thống kê
        stats = dao.diem_stats(semester_id=semester_id, subject_id=subject_id)

        # Tạo workbook Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Thống kê điểm"

        # Thêm thông tin Học kỳ và Môn học
        ws.append(["Học kỳ:", f"{semester.school_year.school_year_name} - {semester.semester_type.name}"])
        ws.append(["Môn học:", subject.subject_name])
        ws.append([])  # Dòng trống

        # Thêm tiêu đề cột
        ws.append(["Điểm", "Số lượng"])

        # Thêm dữ liệu thống kê
        for stat in stats:
            ws.append([stat[0], stat[1]])

        # Lưu workbook vào buffer
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # Trả file Excel về client
        response = Response(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response.headers["Content-Disposition"] = "attachment; filename=thong_ke_diem.xlsx"
        return response

class BangDiemHocKy(BaseView):
    @expose('/', methods=['GET', 'POST'])

    def index(self):
        from app.dao import get_subjects, get_semesters, get_school_years, get_summary_report

        # Lấy dữ liệu cho dropdown
        subjects = get_subjects()
        semesters = get_semesters()
        school_years = get_school_years()

        report_data = None
        selected_subject_id = None
        selected_semester_id = None

        if request.method == 'POST':
            # Lấy dữ liệu từ form
            selected_subject_id = request.form.get('subject_id')
            selected_semester_id = request.form.get('semester_id')

            # Lấy dữ liệu báo cáo
            report_data = get_summary_report(subject_id=selected_subject_id, semester_id=selected_semester_id)

        return self.render(
            'admin/tongketmonhoc.html',
            subjects=subjects,
            semesters=semesters,
            school_years=school_years,
            report_data=report_data,
            selected_subject_id=selected_subject_id,
            selected_semester_id=selected_semester_id
        )

    @expose('/export-pdf', methods=['POST'])
    def export_pdf(self):
        return;

admin.add_view(ClassroomView(Classroom, db.session))
admin.add_view(ApplicationView(ApplicationForm, db.session))
admin.add_view(CurriculumView(Curriculum, db.session))
admin.add_view(StudentInfoView(StudentInfo, db.session))
admin.add_view(RuleView(Rule, db.session))
admin.add_view(SubjectView(Subject, db.session))
admin.add_view(BaseAdminView(User, db.session))
admin.add_view(PhoDiem(name='Phổ điểm', category="Stats"))
admin.add_view(BangDiemHocKy(name='Bảng điểm', category="Stats"))
admin.add_view(LogoutView(name='Logout'))
