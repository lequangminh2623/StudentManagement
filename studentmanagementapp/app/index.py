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

from datetime import datetime

@app.route("/score", methods=['get', 'post'])
def score_input():
    school_years = dao.get_school_years()
    #
    # # Lấy năm học gần nhất
    latest_school_year = None
    # if school_years:
    #     latest_school_year = max(school_years, key=lambda sy: int(sy.school_year_name.split('-')[0]))
    #
    semesters = [
        {"id": 1, "name": "FIRST_TERM"},
        {"id": 2, "name": "SECOND_TERM"}
    ]
    #
    classrooms = []
    subjects = []
    #
    # if current_user.role == Role.TEACHER and latest_school_year:
    #     teacher_info = dao.get_teacher_info_by_user_id(current_user.id)
    #     if teacher_info:
    #         # Lấy các bảng điểm của giáo viên trong năm học gần nhất
    #         transcripts = dao.get_transcripts_by_teacher_and_school_year(teacher_info.id, latest_school_year.id)
    #
    #         classroom_ids = set()
    #         subject_ids = set()
    #
    #         for transcript in transcripts:
    #             classroom_ids.add(transcript.classroom_id)
    #             subject_ids.add(transcript.curriculum.subject_id)
    #
    #         classrooms = [dao.get_classroom_by_id(id) for id in classroom_ids if dao.get_classroom_by_id(id) is not None]
    #         subjects = [dao.get_subject_by_id(id) for id in subject_ids if dao.get_subject_by_id(id) is not None]


    filters = [
        {"name": "School Year", "id": "school-year", "data": school_years},
        {"name": "Semester", "id": "semester", "data": semesters},
        {"name": "Classroom", "id": "classroom", "data": classrooms},
        {"name": "Subject", "id": "subject", "data": subjects}
    ]

    return render_template('score.html', filters=filters, latest_school_year=latest_school_year)



# @login.user_loader
# def load_user(user_id):
#     return dao.get_user_by_id(user_id)
