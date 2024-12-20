from app import db, app, dao
from app.models import *
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask_admin import BaseView, expose
from flask_admin import Admin, AdminIndexView

class TeacherIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render('teacher/index.html')

teacher = Admin(app, name='studentmanagement', template_mode='bootstrap4', index_view=TeacherIndexView())

class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.loai_tai_khoan.__eq__(LoaiTaiKhoan.GIAOVIEN)

@app.route('/teacher/', method=['get', 'post'])
class BangDiemView(AuthenticatedView):
    can_export = True
    column_searchable_list = ['lop_hoc']
    column_filters = ['nam_hoc', 'hoc_ky', 'mon_hoc', 'khoi_lop', 'trang_thai']
    can_view_details = True
    column_list = ['ten_lop', 'si_so', 'khoi_lop', 'nam_hoc', 'hoc_ky', 'mon_hoc', 'trang_thai']


teacher.add_view(BangDiemView(BangDiem, db.session))

