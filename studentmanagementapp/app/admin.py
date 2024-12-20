from app import db, app
from app.models import Transcript, Classroom, Grade, ApplicationForm, Curriculum, ClassroomTransfer, Subject, StudentInfo
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask_admin import BaseView, expose
from flask_admin import Admin, AdminIndexView

admin = Admin(app, name='StudentManagement', template_mode='bootstrap4')

class ApplicationView(ModelView):
    column_list = ['name', 'gender', 'phone', 'address', 'email', 'birthday']
    column_filters = ['status']
    column_default_sort = ('status', True)

class GradeView(ModelView):
    column_list = ['id', 'grade_type', 'school_year']
    column_filters = ['school_year']
    column_searchable_list = ['grade_type']

class ClassroomView(ModelView):
    column_list = ['id', 'classroom_name', 'student_number', 'grade']
    column_filters = ['grade']
    column_searchable_list = ['classroom_name']

class TranscriptView(ModelView):
    can_export = True
    can_view_details = True
    column_list = ['transcript_name', 'is_done', 'classroom', 'score']
    form_excluded_columns = ['is_done']


class CurriculumView(ModelView):
    column_list = ['curriculum_name', 'grade', 'subject']

class ClassroomTransferView(ModelView):
    column_list = ['classroom_id', 'student_id']

class SubjectView(ModelView):
    column_list = ['subject_name']


class StudentInfoView(ModelView):
    column_list = ['name']


admin.add_view(TranscriptView(Transcript, db.session))
admin.add_view(ClassroomView(Classroom, db.session))
admin.add_view(GradeView(Grade, db.session))
admin.add_view(ApplicationView(ApplicationForm, db.session))
admin.add_view(CurriculumView(Curriculum, db.session))
admin.add_views(ClassroomTransferView(ClassroomTransfer, db.session))
admin.add_view(SubjectView(Subject, db.session))
admin.add_view(StudentInfoView(StudentInfo, db.session))