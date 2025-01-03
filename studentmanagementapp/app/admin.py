from datetime import date

from flask_admin import AdminIndexView, expose, Admin, BaseView
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import db, app, dao
from app.dao import get_summary_report, get_subjects, get_semesters, get_school_years
from app.models import Classroom, Grade, Curriculum, \
    Subject, StudentInfo, Rule, Role, User, Semester, SchoolYear, StaffInfo
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect, url_for, flash, request, Response, render_template, make_response, send_file, jsonify


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):

        return self.render('admin/index.html')

admin = Admin(app=app, name='Student Management', template_mode='bootstrap4', index_view=MyAdminIndexView())


class BaseAdminModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role == Role.ADMIN
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')

class BaseAdminView(BaseView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role == Role.ADMIN
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')

class BaseStaffView(BaseView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role == Role.STAFF
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')

class BaseStaffModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role == Role.STAFF
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')

class StudentInfoView(BaseStaffModelView):
    column_list = ['name', 'gender', 'birthday', 'address', 'phone', 'email']
    form_columns = ['name', 'gender', 'birthday', 'address', 'phone', 'email']
    column_searchable_list = ['name']

    def on_model_change(self, form, model, is_created):
        try:
            db.session.add(model)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Student age is not appropriate', 'error')
            return False
        return True

class RuleView(BaseAdminModelView):
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


class CurriculumView(BaseAdminModelView):
    column_list = ['subject', 'grade', 'grade.school_year']
    column_labels = {'grade.school_year': 'School Year'}


class ClassroomView(BaseAdminModelView):
    column_list = ['id', 'classroom_name', 'student_number', 'grade']
    column_filters = ['grade']
    column_searchable_list = ['classroom_name']


class SubjectView(BaseAdminModelView):
    column_list = ['subject_name', '']

class AuthenticatedView(BaseView):
        def is_accessible(self):
            return current_user.is_authenticated


class LogoutView(AuthenticatedView):
    @expose('/')
    def __index__(self):
        logout_user()
        return redirect('/login')

class BangDiemHocKy(BaseAdminView):
    @expose('/get_semesters', methods=['POST'])
    def get_semesters_by_school_year(self):
        school_year_id = request.json.get('school_year_id')  # Lấy id năm học
        if not school_year_id:
            return jsonify({'error': 'Missing school_year_id'}), 400
        # Lọc danh sách học kỳ dựa trên id năm học
        semesters = Semester.query.filter_by(school_year_id=school_year_id).all()
        result = [
            {'id': semester.id, 'name': semester.semester_type.name}  # Trả về id và tên học kỳ
            for semester in semesters
        ]
        return jsonify(result)
    @expose('/', methods=['GET', 'POST'])
    def index(self, **kwargs):
        subjects = get_subjects()
        school_years = get_school_years()
        report_data = []
        selected_subject_id = None
        selected_school_year_id = None
        selected_semester_id = None
        semesters = []

        # Thêm biến chứa tên các giá trị được chọn
        selected_subject = None
        selected_school_year = None
        selected_semester = None

        if request.method == 'POST':
            selected_subject_id = request.form.get('subject_id')
            selected_school_year_id = request.form.get('school_year_id')
            selected_semester_id = request.form.get('semester_id')

            # Truy vấn danh sách các học kỳ của năm học đã chọn
            if selected_school_year_id:
                semesters = Semester.query.filter_by(school_year_id=selected_school_year_id).all()

            # Lọc dữ liệu báo cáo và lấy thông tin các trường đã chọn
            if selected_subject_id:
                selected_subject = Subject.query.filter_by(id=selected_subject_id).first()

            if selected_school_year_id:
                selected_school_year = SchoolYear.query.filter_by(id=selected_school_year_id).first()

            if selected_semester_id:
                selected_semester = Semester.query.filter_by(id=selected_semester_id).first()

            # Nếu có đủ dữ liệu đầu vào, lấy dữ liệu báo cáo
            if selected_subject_id and selected_semester_id:
                report_data = get_summary_report(
                    subject_id=selected_subject_id,
                    semester_id=selected_semester_id
                )

        return self.render(
            'admin/tongketmonhoc.html',
            subjects=subjects,
            school_years=school_years,
            semesters=semesters,
            report_data=report_data,
            selected_subject_id=selected_subject_id,
            selected_school_year_id=selected_school_year_id,
            selected_semester_id=selected_semester_id,
            selected_subject=selected_subject,
            selected_school_year=selected_school_year,
            selected_semester=selected_semester
        )

class Students(BaseStaffView):
    @expose('/', methods=['GET', 'POST'])
    def __index__(self):
        school_year = dao.get_current_school_year()
        classrooms = dao.get_classrooms_by_year_and_grade(school_year.school_year_name)
        filter = {"label": "Classroom", "id": "classroom", "data": classrooms}
        return self.render('admin/students.html', filter=filter)

    @expose('/change_student_classroom', methods=['POST'])
    def change_student_classroom(self):
        try:
            data = request.get_json()
            student_id = data.get('student_id')
            classroom_id = data.get('classroom_id')

            if not student_id or not classroom_id:
                return '', 400

            is_success = dao.change_student_classroom(student_id, classroom_id)

            if is_success:
                flash('Successfully changed classroom!')
                return '', 200
            else:
                return '', 500
        except Exception as e:
            return '', 500

    @expose('/students_in_classroom', methods=['GET', 'POST'])
    def students_in_classroom(self):
        try:
            data = request.json
            classroom_id = data.get('classroom_id')
            kw = request.args.get('kw', None)

            if not classroom_id:
                return jsonify({"error": "Không có classroom_id"}), 400

            # Lấy danh sách học sinh từ DAO
            students = dao.get_students_by_classroom(classroom_id, kw)
            classrooms = dao.get_classroom_in_same_grade(classroom_id)

            if not students:
                return jsonify({"error": "Không tìm thấy học sinh nào cho lớp học này"}), 404

            # Lấy sĩ số lớp từ DAO
            total_students = dao.get_classroom_and_student_count(classroom_id)

            students_data = [
                {
                    "id": student.id,
                    "name": student.name,
                    "gender": student.gender.name,  # Enum cần chuyển đổi sang chuỗi
                    "phone": student.phone,
                    "address": student.address,
                    "email": student.email,
                    "birthday": student.birthday.strftime('%d-%m-%Y'),
                }
                for student in students
            ]

            return jsonify({
                "students": students_data,
                "total_students": total_students,
                "classrooms": classrooms
            }), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "An error occurred"}), 500

    @expose('/get_classroom_id', methods=['GET', 'POST'])
    def get_classroom_id(self):
        try:
            data = request.json
            school_year = dao.get_current_school_year()
            school_year_name = school_year.school_year_name
            classroom_name = data.get("classroom_name")
            classroom_id = dao.get_classrooms_id_by_school_year_name_and_classroom_name(school_year_name,
                                                                                        classroom_name)
            if classroom_id:
                return jsonify({"classroom_id": classroom_id})
            else:
                return jsonify({"error": "Classroom not found"}), 404
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "An error occurred"}), 500

class AutoArrangeClass(BaseStaffView):
    @expose('/')
    def index(self):
        return self.render('admin/auto_arrange_class.html')

    @expose('/arrange', methods=['POST'])
    def arrange(self):
        try:
            success = dao.auto_arrange_classes()
            if success:
                flash('Classes have been auto-arranged successfully!', 'success')
            else:
                flash('Failed to auto-arrange classes.', 'error')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('autoarrangeclass.index'))



admin.add_view(AutoArrangeClass(name='Auto Arrange Classes', endpoint='autoarrangeclass'))
admin.add_view(ClassroomView(Classroom, db.session))
admin.add_view(CurriculumView(Curriculum, db.session))
admin.add_view(StudentInfoView(StudentInfo, db.session))
admin.add_view(RuleView(Rule, db.session))
admin.add_view(SubjectView(Subject, db.session))
admin.add_view(BaseAdminModelView(User, db.session))
admin.add_view(BangDiemHocKy(name='Stats'))
admin.add_view(Students(name='Class List'))
admin.add_view(LogoutView(name='Logout'))