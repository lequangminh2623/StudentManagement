from app import app
import hashlib
# from models import User


# def auth_user(username, password):
#     password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
#
#     return User.query.filter(User.username.__eq__(username),
#                              User.password.__eq__(password)).first()

# def get_user_by_id(id):
#     return User.query.get(id)