# from flask import Flask
# from config import Config
# from extensions import db

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     db.init_app(app) # DB 연결

#     # 블루프린트 등록
#     from app.routes.auth import auth_bp
#     app.register_blueprint(auth_bp)

#     from app.routes.fridge_views import fridge_views_bp
#     from app.routes.fridge import fridge_bp
#     app.register_blueprint(fridge_views_bp)
#     app.register_blueprint(fridge_bp)

#     return app





# from flask import Flask
# # 더 이상 존재하지 않는 config나 extensions 대신, 새로 만든 통합 파일을 임포트해.
# from database import init_database

# def create_app():
#     app = Flask(__name__)

#     # 데이터베이스 연동, .env 환경변수 로드, 테이블 생성을 이 한 줄로 끝내!
#     init_database(app)

#     # 블루프린트 등록
#     from app.routes.auth import auth_bp
#     app.register_blueprint(auth_bp)

#     from app.routes.fridge_views import fridge_views_bp
#     from app.routes.fridge import fridge_bp
#     app.register_blueprint(fridge_views_bp)
#     app.register_blueprint(fridge_bp)

#     return app


# 3차수정

from flask import Flask, url_for as flask_url_for
from database import init_database
from pathlib import Path

def create_app():
    # 🚨 수정된 부분: 템플릿과 정적 파일의 위치가 상위 폴더(../)에 있음을 Flask에 명시
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # 데이터베이스 연동, .env 환경변수 로드, 테이블 생성
    init_database(app)

    # 이미지 업로드 폴더 세팅 (상위 폴더의 static 기준)
    app.config["UPLOAD_FOLDER"] = str(Path("../static") / "uploads")
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    # 블루프린트 등록
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.fridge_views import fridge_views_bp
    from app.routes.fridge import fridge_bp
    from app.routes.payment_toss import payment_toss_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(fridge_views_bp)
    app.register_blueprint(fridge_bp)
    app.register_blueprint(payment_toss_bp)

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
                'recipeDetailPage': 'main.recipeDetailPage',
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