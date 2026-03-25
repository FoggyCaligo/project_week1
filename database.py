import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# 1. DB 객체 생성
db = SQLAlchemy()

def init_database(app):
    """
    Flask 앱 객체를 받아 DB 설정, 연동, 테이블 생성을 한 번에 처리합니다.
    """
    # 2. 환경 변수 로드 (.env 파일 참조)
    load_dotenv()
    
    # 하드코딩된 기본값(fallback)을 모두 제거하고 순수하게 환경변수만 가져옵니다.
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '3306')  # 포트는 기본적으로 3306을 많이 쓰므로 문자열로 기본값 부여
    db_name = os.getenv('DB_NAME')
    secret_key = os.getenv('SECRET_KEY')
    
    # 보안 안전장치: 필수 설정값이 하나라도 .env에 없으면 서버 실행을 멈추고 에러 표시
    if not all([db_user, db_password, db_host, db_name, secret_key]):
        raise ValueError("환경 변수(.env)에 필수 데이터베이스 접속 정보나 SECRET_KEY가 누락되었습니다. .env 파일을 확인해주세요.")
    
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = secret_key
    
    # 3. app에 db 연동
    db.init_app(app)
    
    # 4. DB 테이블 자동 생성
    with app.app_context():
        # 테이블을 생성하려면 여기서 모델들을 임포트해야 합니다.
        try:
            from app.models.ingredient import UserIngredient
            # 필요한 다른 모델들도 여기에 추가 (ex: from app.models.user import User 등)
        except ImportError:
            pass
            
        db.create_all()
        print("Database settings applied and tables created successfully!")