from database import db
from sqlalchemy.sql import func

class User(db.Model):
    __tablename__ = 'users'

    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='사용자 고유 ID')
    userName = db.Column(db.String(255), nullable=False, unique=True , comment='로그인 아이디')
    passwordHash = db.Column(db.String(255), nullable=False, comment='비밀번호 해시')
    nickName = db.Column(db.String(255), nullable=False, comment='닉네임')
    createdAt = db.Column(db.DateTime, server_default=func.current_timestamp(), comment='가입일')

    # 관계 설정 (역참조)
    ingredients = db.relationship('UserIngredient', backref='user', lazy=True, cascade="all, delete-orphan")
    # bookmarks = db.relationship('Bookmark', backref='user', lazy=True, cascade="all, delete-orphan")
    # posts = db.relationship('SocialPost', backref='user', lazy=True, cascade="all, delete-orphan")