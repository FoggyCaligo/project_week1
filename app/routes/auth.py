from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # 1. 폼 데이터 가져오기 (login.html/signup.html의 name 속성 확인!)
        username = request.form.get('userName')
        nickname = request.form.get('nickName')
        password = request.form.get('password')
        
        # 2. 서비스 호출 (방금 만드신 staticmethod!)
        success = AuthService.signup_user(username, nickname, password)
        
        if success:
            # 회원가입 성공하면 로그인으로!
            return redirect(url_for('auth.login'))
        else:
            # 중복된 아이디면 다시 회원가입 페이지로 (나중에 에러 메시지 띄우면 좋아요)
            return redirect(url_for('auth.signup'))
            
    return render_template('signup.html')
# 주소는 하나! 방식(methods)은 두 개 다 받기!
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 1. 화면만 보고 싶을 때 (주소창에 엔터 쳤을 때)
    if request.method == 'GET':
        return render_template('login.html')

    # 2. 아이디/비번 치고 버튼 눌렀을 때 (POST)
    username = request.form.get('userName', '').strip()
    password = request.form.get('password', '').strip()

    # 서비스 레이어(MariaDB 조회) 호출
    user = AuthService.login_user(username, password)
    
    if user:
        session['userID'] = user.ID
        session['userName'] = user.userName
        flash("로그인되었습니다.", "success")
        return redirect(url_for('test.home')) # 메인 페이지로 이동
    
    flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")
    # 실패하면 다시 로그인 페이지로! (함수 이름이 'login'이니까 url_for('auth.login'))
    return redirect(url_for('auth.login'))

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("로그아웃되었습니다.", "success")
    return redirect(url_for('auth.login'))
