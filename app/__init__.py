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

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(fridge_views_bp)
    app.register_blueprint(fridge_bp)

    # 화면 우측 상단에 유저 닉네임을 띄우기 위한 컨텍스트 주입
    from app.services.authService import AuthService
    @app.context_processor
    def injectCommonData():
        return {"currentUser": AuthService.getCurrentUser()}

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