from flask import Flask
from config import Config
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app) # DB 연결

    # 블루프린트 등록
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.fridge_views import fridge_views_bp
    from app.routes.fridge import fridge_bp
    app.register_blueprint(fridge_views_bp)
    app.register_blueprint(fridge_bp)

    return app
