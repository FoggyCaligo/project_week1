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
    from app.routes.fridge_views import fridge_views_bp
    from app.routes.fridge import fridge_bp
    from app.routes.recipe import recipe_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(fridge_views_bp)
    app.register_blueprint(fridge_bp)
    app.register_blueprint(recipe_bp)

    # 화면 우측 상단에 유저 닉네임을 띄우기 위한 컨텍스트 주입
    from app.common import getCurrentUser
    @app.context_processor
    def injectCommonData():
        return {"currentUser": getCurrentUser()}

    # 🚨 핵심 포인트: 기존 HTML들의 url_for 라우트 에러를 방지하는 어댑터!
    @app.context_processor
    def override_url_for():
        def custom_url_for(endpoint, **values):
            # 옛날 방식의 라우트 이름을 블루프린트 이름으로 자동 치환
            mapping = {
                'loginPage': 'auth.loginPage',
                'signupPage': 'auth.signupPage',
                'logout': 'auth.logout',
                'home': 'main.home',
                'searchPage': 'main.searchPage',
                'recommendPage': 'main.recommendPage',
                'recipeDetailPage': 'recipe.recipeDetailPage',
                'addBookmark': 'main.addBookmark',
                'bookmarksPage': 'main.bookmarksPage',
                'removeBookmark': 'main.removeBookmark',
                'socialPage': 'main.socialPage',
                'createSocialPost': 'main.createSocialPost',
            }
            if endpoint in mapping:
                endpoint = mapping[endpoint]
            return flask_url_for(endpoint, **values)
        return dict(url_for=custom_url_for)

    return app