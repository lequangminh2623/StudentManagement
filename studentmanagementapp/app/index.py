from flask import render_template, request
from werkzeug.utils import redirect
from app import dao, utils
import math
from flask_login import login_user, current_user
from app.models import *


@app.route("/")
def index():

    return render_template('index.html')


@app.route("/login", methods=['get', 'post'])
def login_process():

    return render_template('login.html')

@app.route("/score", methods=['get', 'post'])
def score_input():
    school_years = dao.get_school_years()
    semesters = dao.get_semesters()
    classrooms = dao.get_classrooms()
    subjects = dao.get_subjects()

    filters = [
        {"name": "School Year", "id": "school-year", "data": school_years},
        {"name": "Semester", "id": "semester", "data": semesters},
        {"name": "Classroom", "id": "classroom", "data": classrooms},
        {"name": "Subject", "id": "subject", "data": subjects}
    ]

    return render_template('score.html', filters=filters)



# @login.user_loader
# def load_user(user_id):
#     return dao.get_user_by_id(user_id)
