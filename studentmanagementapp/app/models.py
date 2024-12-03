from sqlalchemy import Column, Integer, Float, String, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship, Relationship
from __init__ import db, app
from enum import Enum as RoleEnum
import hashlib

class User(db.Model):
    pass



if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        db.session.add()
        db.session.commit()