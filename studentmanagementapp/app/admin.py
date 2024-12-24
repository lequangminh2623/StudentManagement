from app import db, app
from app.models import Classroom, Grade, ApplicationForm, Curriculum, \
    Subject, StudentInfo, Rule, ApplicationFormStatus, Score, Role, User
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask_admin import Admin, BaseView, expose
from flask import redirect, url_for, flash

admin = Admin(app, name='StudentManagement', template_mode='bootstrap4')

class BaseAdminView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role == Role.ADMIN
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




admin.add_view(ClassroomView(Classroom, db.session))
admin.add_view(ApplicationView(ApplicationForm, db.session))
admin.add_view(CurriculumView(Curriculum, db.session))
admin.add_view(StudentInfoView(StudentInfo, db.session))
admin.add_view(RuleView(Rule, db.session))
admin.add_view(SubjectView(Subject, db.session))
admin.add_view(BaseAdminView(User, db.session))
admin.add_view(LogoutView(name='Logout'))