from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy() # DB 관리

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

    # config.py가 없거나 부족할 경우 환경변수 로드
    from dotenv import load_dotenv
    load_dotenv()
    
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not db_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{os.getenv('DB_USER', 'kool')}:{os.getenv('DB_PASSWORD', 'master')}@{os.getenv('DB_HOST', '43.201.47.181')}:3306/{os.getenv('DB_NAME', 'cloud33')}?charset=utf8mb4"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")

    db.init_app(app) # DB 연결

    # 블루프린트 등록
    try:
        from app.routes.auth import auth_bp
        app.register_blueprint(auth_bp)
    except ImportError:
        pass
        
    from app.routes.fridge import fridge_view_bp, fridge_api_bp
    from app.routes.bmi import bmi_bp
    
    app.register_blueprint(fridge_view_bp)
    app.register_blueprint(fridge_api_bp)
    app.register_blueprint(bmi_bp)

    return app
