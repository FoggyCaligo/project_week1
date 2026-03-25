from app.models.user import User
from werkzeug.security import check_password_hash, generate_password_hash
from app import db

class AuthService:
    @staticmethod
    def login_user(username, password):
        # 1. DB에서 유저 찾기 findbyusername
        user = User.query.filter_by(userName=username).first()
        
        # 2. 비밀번호 확인 
        if user and check_password_hash(user.passwordHash, password):
            return user
        return None

    @staticmethod
    def signup_user(username, nickname, password):
        # 중복 체크 후 저장
        if User.query.filter_by(userName=username).first():
            return False
        new_user = User(
            userName=username,
            nickName=nickname,
            passwordHash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        return True