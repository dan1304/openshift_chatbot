from flask_sqlalchemy import SQLAlchemy
from app import db


class Kbs(db.Model):
    __tablename__ = 'kbs'
    kbs_id = db.Column(db.Integer, primary_key=True)
    kbs_desc = db.Column(db.String(1664), index=True, unique=False)
    kbs_resolution = db.Column(db.String(1664), index=True)
    kbs_tag = db.Column(db.String(1000))

    def __init__(self, kbs_desc, kbs_resolution, kbs_tag):
        self.kbs_desc = kbs_desc
        self.kbs_resolution = kbs_resolution
        self.kbs_tag = kbs_tag

    def to_dict(self):
        return {
            'kbs_id': self.kbs_id,
            'kbs_desc': self.kbs_desc,
            'kbs_resolution': self.kbs_resolution,
            'kbs_tag': self.kbs_tag
        }

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(64), unique=True)
    user_password = db.Column(db.String(64))
    # is_active = db.Column(Boolean, , default=True)

    def __init__(self, user_id, user_name, user_password):
        self.user_id = self.user_id
        self.user_name = self.user_name
        self.user_password = self.user_password

