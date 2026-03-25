from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy() # DB 관리

def create_app():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    app = Flask(__name__,static_folder='../static', template_folder=template_dir)
    app.config.from_object(Config)

    db.init_app(app) # DB 연결

    # 블루프린트 등록
    from app.routes.auth import auth_bp
    from app.routes.test import test_bp
    
    app.register_blueprint(test_bp)
    app.register_blueprint(auth_bp)
    
    
    return app