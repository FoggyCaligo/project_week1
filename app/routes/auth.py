# from flask import Blueprint
# auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/')
# def index():
#     return "<h1>서버 작동 </h1>"

# 로그인 회원가입 일단 넣었음

from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from app.common import findUserByUserName, getNextID, getNow, users

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def loginPage():
    if request.method == "POST":
        userName = request.form.get("userName", "").strip()
        password = request.form.get("password", "").strip()

        foundUser = findUserByUserName(userName)
        if foundUser is None or not check_password_hash(foundUser["passwordHash"], password):
            flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")
            return redirect(url_for("auth.loginPage"))

        session["userID"] = foundUser["id"]
        flash("로그인되었습니다.", "success")
        return redirect(url_for("main.home"))

    return render_template("login.html")

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

        if findUserByUserName(userName):
            flash("이미 사용 중인 아이디입니다.", "error")
            return redirect(url_for("auth.signupPage"))

        users.append({
            "id": getNextID(users), "userName": userName, "passwordHash": generate_password_hash(password),
            "nickName": nickName, "createdAt": getNow(),
        })

        flash("회원가입이 완료되었습니다. 로그인해주세요.", "success")
        return redirect(url_for("auth.loginPage"))

    return render_template("signup.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("로그아웃되었습니다.", "success")
    return redirect(url_for("main.home"))