# 냉장고 파트 고도화 (이미지 적용 및 버그 픽스)

다음 파일들이 냉장고 기능 고도화(재료별 사진 매핑) 및 500 에러 수정을 위해 수정되었습니다.

1. `app/routes/fridge_views.py`
   - 비로그인 상태에서 '/fridge' 진입 시 리다이렉트하는 코드를 기존 `loginPage`에서 새로운 블루프린트 구조인 `auth.login`으로 변경하여 500 에러 방지.

2. `app/models/ingredient.py`
   - `UserIngredient.to_dict()` 메서드를 확장하여 식재료 이름(`ingredientName`)에 해당하는 이미지를 매핑하여 `image_url` 필드로 반환하도록 구현.
   - 두부, 계란, 당근, 양파, 마늘 등 주요 식재료에 대해 무료 고화질 이미지(Unsplash) URL 매핑. (해당 없는 경우 기본 이미지 표시)

5. `templates/fridge.html` (UI/UX 추가 고도화 및 dev 병합)
   - `dev` 브랜치에 업데이트된 식재료 추가 폼(`fridgeAddForm`)의 최신 디자인을 병합하여 반영했습니다.
   - 기존의 투박한 브라우저 `alert` 대신, 부드럽게 나타났다가 사라지는 자체 **Toast 알림 UI**를 적용하여 사용자 경험을 크게 개선했습니다.
   - 유통기한 입력 시 **오늘 날짜 이전은 선택할 수 없도록** 달력(min 속성)을 제한했습니다.
   - 동일한 식재료를 수량(N개)으로 그룹화해서 보여주는 카드형 디자인이 유지되도록 최적화했습니다.

7. `templates/fridge.html` (동일 식재료 그룹 뱃지 디자인 수정)
   - 동일 식재료 그룹 카드에 "유통기한 임박" 상태가 아닐 때 뱃지가 아닌 일반 텍스트 형태로 "신선 보관중"을 표시하도록 개선하여 시각적 불편함을 줄였습니다.

4. `app/services/fridge_service.py`
   - 식재료 추가(`add_ingredient`), 수정(`edit_ingredient`), 삭제(`delete_ingredient`) 시 `SQLAlchemy` ORM 객체의 외래키 바인딩 에러를 방지하기 위해 `원시 SQL(Raw SQL)`을 사용하도록 로직을 변경하여 500 에러 및 400 에러를 수정했습니다.
   - 추가·수정 시 `category`를 허용 목록(채소·과일·육류·수산물·유제품·가공식품·기타)으로 검증 후 DB에 저장합니다. 수정 요청에 `category` 필드가 없으면 기존 값을 유지합니다.

8. 분류(category) 저장·표시 버그 수정 (`app/models/ingredient.py`, `app/routes/fridge.py`, `app/routes/fridge_views.py`, `templates/fridge.html`)
   - 프론트에서 선택한 분류가 API 요청 본문에 포함되지 않아 항상 `기타`로 보이던 문제: `POST /api/fridge/add`·`PUT /api/fridge/edit`에 `category`를 전달하고, `userIngredients.category` 컬럼에 저장하며, `to_dict()`의 `category`로 내려줍니다.
   - **공용 DB(`userIngredients`)에 `category` 컬럼이 없으면** 아래를 한 번 실행해야 합니다.  
     `ALTER TABLE userIngredients ADD COLUMN category VARCHAR(32) NULL COMMENT '분류' AFTER expireDate;`
   - 냉장고 메인 그리드 카드(동일 재료 그룹)에도 분류명을 한 줄로 표시하며, 그룹 내 분류가 여러 개면 `채소 · 과일`처럼 구분해 표시합니다.
