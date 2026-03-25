from app.models.user import User
from werkzeug.security import check_password_hash, generate_password_hash
from database import db
from flask import session

class AuthService:
    @staticmethod
    def login_user(userName, password):
        # 1. DB에서 유저 찾기 findbyusername
        user = User.query.filter_by(userName=userName).first()
        
        # 2. 비밀번호 확인 
        if user and check_password_hash(user.passwordHash, password):
            return user
        return None

    @staticmethod
    def signup_user(userName, nickName, password):
        # 중복 체크 후 저장
        if User.query.filter_by(userName=userName).first():
            return False
        if User.query.filter_by(nickName=nickName).first():
            return False
        
        new_user = User(
            userName=userName,
            nickName=nickName,
            passwordHash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        return True
    @staticmethod
    def getCurrentUser():
        userId = session.get("userID")
        if not userId:
            return None
        return User.query.get(userId)
    @staticmethod
    def findUserByUserName(userName):
        return User.query.filter_by(userName=userName).first()
    @staticmethod
    def findUserByNickName(nickName):
        return User.query.filter_by(nickName=nickName).first()
    @staticmethod
    def findUserByID(userID):
        return User.query.get(userID)