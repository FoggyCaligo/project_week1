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
    # app/services/authService.py 맨 아래에 추가

    @staticmethod
    def requireLogin():
        """
        [로그인 필수 체크] 
        로그인 안 되어 있으면 로그인 페이지로 보낼 준비물(redirect)을,
        로그인 되어 있으면 유저 객체(user)를 리턴합니다.
        """
        from flask import redirect, url_for, flash
        
        user = AuthService.getCurrentUser()
        if not user:
            flash("로그인이 필요한 서비스입니다.", "info")
            # 여기서 url_for 안의 'auth.loginPage'는 실제 로그인 라우트 이름으로 맞추셔야 합니다!
            return None, redirect(url_for('auth.loginPage')) 
        
        # 로그인 성공 시 (유저객체, 리다이렉트 없음)
        return user, None