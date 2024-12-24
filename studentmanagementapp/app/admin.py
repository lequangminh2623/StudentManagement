from app import db, app
from app.models import Transcript, Classroom, Grade, ApplicationForm, Curriculum, \
    ClassroomTransfer, Subject, StudentInfo, Rule, ApplicationFormStatus, Score
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask_admin import BaseView, expose
from flask_admin import Admin, AdminIndexView
from flask import redirect, url_for, flash
from wtforms.fields import DecimalField
from wtforms.widgets import NumberInput
from wtforms import validators
from flask_admin.model.form import InlineFormAdmin
from flask_login import current_user

admin = Admin(app, name='StudentManagement', template_mode='bootstrap4')

class xacThucView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role

class ApplicationView(ModelView):
    column_list = ['name', 'gender', 'phone', 'address', 'email', 'birthday', 'status']
    column_filters = ['status', 'birthday']
    column_searchable_list = ['name']
    column_default_sort = ('status', True)

    def on_model_change(self, form, model, is_created):
        pass


class RuleView(ModelView):
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


class CurriculumView(ModelView):
    column_list = ['subject', 'grade', 'grade.school_year']
    column_labels = {'grade.school_year': 'School Year'}


# class ScoreInlineForm(InlineFormAdmin):
#     form_overrides = {
#         'score_number': DecimalField
#     }
#     form_args = {
#         'score_number': {
#             'label': 'Điểm',
#             'validators': [
#                 validators.NumberRange(min=0, max=10, message='Điểm phải từ 0 đến 10')
#             ],
#             'widget': NumberInput(min=0, max=10, step=0.1)
#         }
#     }
#     form_columns = ['score_number', 'score_type', 'student_info']
#     form_labels = {
#         'score_number': 'Điểm',
#         'score_type': 'Loại điểm',
#         'student_info': 'Học sinh'
#     }


class TranscriptView(ModelView):
    # inline_models = [ScoreInlineForm(Score)] # Tạo instance của ScoreInlineForm và truyền vào
    # column_labels = {
    #     'teacher_info': 'Teacher'
    # }
    # form_excluded_columns = ('scores',)
    column_list = ['transcript_name']





class ClassroomTransferView(ModelView):
    column_list = ['classroom_id', 'student_info_id']

class StudentInfoView(ModelView):
    column_list = ['name']

class ClassroomView(ModelView):
    column_list = ['id', 'classroom_name', 'student_number', 'grade']
    column_filters = ['grade']
    column_searchable_list = ['classroom_name']




admin.add_view(ClassroomView(Classroom, db.session))
admin.add_view(ApplicationView(ApplicationForm, db.session))
admin.add_view(CurriculumView(Curriculum, db.session))
admin.add_views(ClassroomTransferView(ClassroomTransfer, db.session))
admin.add_view(StudentInfoView(StudentInfo, db.session))
admin.add_view(RuleView(Rule, db.session))
admin.add_view(TranscriptView(Transcript, db.session))