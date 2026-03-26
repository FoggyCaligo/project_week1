# from flask import Blueprint
# auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/')
# def index():
#     return "<h1>서버 작동 </h1>"

# 로그인 회원가입 일단 넣었음

from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from app.common import  getNextID, getNow, users
from app.services.authService import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def loginPage():
    if request.method == "POST":
        userName = request.form.get("userName", "").strip()
        password = request.form.get("password", "").strip()

        user = AuthService.login_user(userName, password)
        if user:
            session['userID'] = user.ID
            session['userName'] = user.userName
            flash("로그인되었습니다.", "success")
            return redirect(url_for('main.home')) # 메인 페이지로 이동
        else:
            flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")
            # 실패하면 다시 로그인 페이지로! (함수 이름이 'login'이니까 url_for('auth.login'))
            return redirect(url_for('auth.loginPage'))
    else:
        return render_template('login.html')
        
@auth_bp.route("/check-duplicate", methods=["POST"])
def checkDuplicate():
    data = request.get_json()
    field = data.get("field") # "userName" 또는 "nickName"
    value = data.get("value", "").strip()
    
    if not value:
        return {"result": "empty", "message": "내용을 입력해주세요."}, 400
        
    if field == "userName":
        exists = AuthService.findUserByUserName(value)
        msg_type = "아이디"
    else:
        exists = AuthService.findUserByNickName(value)
        msg_type = "닉네임"
        
    if exists:
        return {"result": "fail", "message": f"이미 사용 중인 {msg_type}입니다."}, 200
    else:
        return {"result": "success", "message": f"사용 가능한 {msg_type}입니다."}, 200
@auth_bp.route("/signup", methods=["GET", "POST"])
def signupPage():
    if request.method == "POST":
        userName = request.form.get("userName", "").strip()
        nickName = request.form.get("nickName", "").strip()
        password = request.form.get("password", "").strip()
        passwordConfirm = request.form.get("passwordConfirm", "").strip()

        if not userName or not nickName or not password:
            flash("모든 항목을 입력해주세요.", "error")
            return redirect(url_for("auth.signupPage"))

        if password != passwordConfirm:
            flash("비밀번호 확인이 일치하지 않습니다.", "error")
            return redirect(url_for("auth.signupPage"))

        success = AuthService.signup_user(userName, nickName, password)
        
        if success:
            flash("회원가입이 완료되었습니다. 로그인해주세요.", "success")
            return redirect(url_for("auth.loginPage"))
        else:
            flash("이미 사용 중인 아이디입니다.", "error")
            return redirect(url_for("auth.signupPage"))
    else:
        return render_template("signup.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("로그아웃되었습니다.", "success")
    return redirect(url_for("main.home"))