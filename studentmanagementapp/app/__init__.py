import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from urllib.parse import quote
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = "HKJ68$^&JH*%568HNNMK"
app.config["SQLALCHEMY_DATABASE_URI"]="mysql+pymysql://root:%s@localhost/studentmanagementdb?charset=utf8mb4" % quote(os.getenv("DB_PASSWORD"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 5



db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app=app)
login.login_view = 'login_process'



cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True
)

