from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'  

    ID = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(50), unique=True, nullable=False)
    passwordHash = db.Column(db.String(255), nullable=False)
    nickName = db.Column(db.String(50))
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)