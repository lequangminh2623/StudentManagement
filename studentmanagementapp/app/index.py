from flask import render_template, request
from werkzeug.utils import redirect
import dao
from __init__ import app
import math
from flask_login import login_user
from models import *


@app.route("/")
def index():

    return render_template('index.html')


@app.route("/login", methods=['get', 'post'])
def login_process():

    return render_template('login.html')

@app.route("/score", methods=['get', 'post'])
def score_input():

    return render_template('scoreformselection.html')

# @login.user_loader
# def load_user(user_id):
#     return dao.get_user_by_id(user_id)



if __name__ == '__main__':
    import admin
    app.run(debug=True)