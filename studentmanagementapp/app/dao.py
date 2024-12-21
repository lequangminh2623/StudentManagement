from sqlalchemy.sql.operators import contains

from app import app
import hashlib

from app.models import SchoolYear, Semester, Classroom, Subject


# from models import User


# def auth_user(username, password):
#     password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
#
#     return User.query.filter(User.username.__eq__(username),
#                              User.password.__eq__(password)).first()

# def get_user_by_id(id):
#     return User.query.get(id)

def get_school_years():
    return SchoolYear.query.order_by(-SchoolYear.id).all()

def get_semesters():
    return Semester.query.all()

def get_classrooms(kw=None):
    query = Classroom.query
    if kw:
        query = query.filter(Classroom.classroom_name.ilike(kw))
    return query.order_by().all()

def get_subjects():
    query = Subject.query
    return query.all()