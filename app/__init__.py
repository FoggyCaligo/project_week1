from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy() # DB 관리

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app) # DB 연결

    # 블루프린트 등록
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app