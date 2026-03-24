# 🚀 전체 통합 프론트/백엔드 로컬 테스트 가이드

본 문서는 `dev` 브랜치의 프론트엔드 모놀리식 구조(단일 `app.py`)에 냉장고 파트(팀원2)의 Blueprint API 로직을 통합한 후, 로컬에서 전체 시스템을 테스트하기 위한 환경 세팅 및 실행 가이드입니다.

## 🛠️ 통합 테스트 환경 세팅 방법 (최초 1회)

**1. 최신 통합 코드 가져오기 (`local_jang` 브랜치 병합)**
```powershell
git fetch origin
git merge origin/local_jang
```

**2. 가상환경 활성화 및 라이브러리 설치**
```powershell
# 가상환경 활성화
.\venv\Scripts\activate

# 의존성 패키지 설치 (SQLAlchemy 연동 포함)
pip install -r requirements.txt
```

**3. 원격 DB 환경변수 설정**
프로젝트 루트 경로에 `.env` 파일이 존재해야 하며, 아래 환경 변수가 설정되어 있어야 합니다.
* `DB_USER`
* `DB_PASSWORD`
* `DB_HOST`
* `DB_NAME`
* `SECRET_KEY`

**4. 데이터베이스 테이블 초기화**
(최초 구동 시 냉장고 관련 신규 테이블 스키마 적용을 위해 실행 필요)
```powershell
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
```

---

## 💻 서버 실행 및 기능 확인

**1. 서버 실행**
기존 실행 방식과 동일하게 `app.py`를 실행합니다.
```powershell
python app.py
```

**2. 라우팅 및 기능 동작 테스트**
* 접속: `http://127.0.0.1:5000/`
* 점검 사항:
  * 홈 화면 및 서브 페이지 정상 렌더링 여부 확인
  * `/fridge` 경로 (내 냉장고 페이지) 진입 시 실제 MariaDB 데이터 연동 확인
  * 식재료 추가 및 삭제 API 동작 및 D-Day 시각화 확인

> **[참고 사항]**
> * 기존 `app.py`의 다른 라우터 로직은 일절 수정하지 않았으며, `/fridge` 관련 엔드포인트만 Blueprint 구조(`app/routes/fridge.py`, `app/routes/fridge_views.py`)로 이관하여 통합되었습니다.
> * 프론트엔드 `fridge.html`은 제공된 디자인을 유지하되, 백엔드 변수 맵핑만 조정되었습니다.
