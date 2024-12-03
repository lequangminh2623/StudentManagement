from flask import render_template, request
from werkzeug.utils import redirect
import dao
from __init__ import app, login
import math
from flask_login import login_user


@app.route("/")
def index():

    return render_template('index.html')


@app.route("/login", methods=['get', 'post'])
def login_process():

    return render_template('login.html')

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)



if __name__ == '__main__':
    app.run(debug=True)