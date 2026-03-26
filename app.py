from app import create_app

# app 폴더의 __init__.py에 있는 create_app() 함수를 호출해서 앱을 생성해.
app = create_app()

# app.config['WTF_CSRF_ENABLED'] = False  # 임시로 보안 해제!

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True)