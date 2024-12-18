from __init__ import db, app
from models import Transcript
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask_admin import BaseView, expose
from flask_admin import Admin, AdminIndexView

teacher = Admin(app, name='studentmanagement', template_mode='bootstrap4', index_view=AdminIndexView())

@app.route('/teacher/', methods=['get', 'post'])
class BangDiemView(ModelView):
    can_export = True
    # column_searchable_list = ['']
    # column_filters = ['']
    can_view_details = True
    column_list = '__all__'


teacher.add_view(BangDiemView(Transcript, db.session))
