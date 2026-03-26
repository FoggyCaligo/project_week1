from flask import Flask, url_for as flask_url_for
from database import init_database
from pathlib import Path

def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    # 데이터베이스 연동, .env 환경변수 로드, 테이블 생성
    init_database(app)

    # 이미지 업로드 폴더 세팅
    app.config["UPLOAD_FOLDER"] = str(Path(app.static_folder) / "uploads")
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    # 블루프린트 등록
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.fridge_views import fridge_views_bp
    from app.routes.fridge import fridge_bp
    from app.routes.bookmarks import bookmarks_bp
    from app.routes.social import social_bp
    from app.routes.recipe import recipe_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(fridge_views_bp)
    app.register_blueprint(fridge_bp)
    app.register_blueprint(bookmarks_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(recipe_bp)

    # 화면 우측 상단에 유저 닉네임을 띄우기 위한 컨텍스트 주입
    from app.services.authService import AuthService
    @app.context_processor
    def injectCommonData():
        return {"currentUser": AuthService.getCurrentUser()}

    # 기존 템플릿 url_for 호환 어댑터
    @app.context_processor
    def override_url_for():
        def custom_url_for(endpoint, **values):
            mapping = {
                "loginPage": "auth.loginPage",
                "signupPage": "auth.signupPage",
                "logout": "auth.logout",

                "home": "main.home",
                "searchPage": "main.searchPage",
                "recommendPage": "main.recommendPage",
                "recipeDetailPage": "recipe.recipeDetailPage",

                "addBookmark": "bookmarks.addBookmark",
                "bookmarksPage": "bookmarks.bookmarksPage",
                "removeBookmark": "bookmarks.removeBookmark",

                "socialPage": "social.socialPage",
                "createSocialPost": "social.createSocialPost",
            }
            if endpoint in mapping:
                endpoint = mapping[endpoint]
            return flask_url_for(endpoint, **values)
        return dict(url_for=custom_url_for)

    return app