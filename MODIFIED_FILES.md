# 냉장고 파트 고도화 (이미지 적용 및 버그 픽스)

다음 파일들이 냉장고 기능 고도화(재료별 사진 매핑) 및 500 에러 수정을 위해 수정되었습니다.

1. `app/routes/fridge_views.py`
   - 비로그인 상태에서 '/fridge' 진입 시 리다이렉트하는 코드를 기존 `loginPage`에서 새로운 블루프린트 구조인 `auth.login`으로 변경하여 500 에러 방지.

2. `app/models/ingredient.py`
   - `UserIngredient.to_dict()` 메서드를 확장하여 식재료 이름(`ingredientName`)에 해당하는 이미지를 매핑하여 `image_url` 필드로 반환하도록 구현.
   - 두부, 계란, 당근, 양파, 마늘 등 주요 식재료에 대해 무료 고화질 이미지(Unsplash) URL 매핑. (해당 없는 경우 기본 이미지 표시)
   - **사과·배·바나나·토마토·오이** 등 매핑 추가, 기본 이미지는 향신료 사진이 아닌 일반 식재료 느낌으로 교체. 매칭 시 **키 길이 내림차순**으로 검사해 `대파`/`파` 등 우선순위 정리.
   - `image_map`에 없는 재료는 **`category`별 공통 이미지**(`CATEGORY_DEFAULT_IMAGES`: 채소·과일·육류·수산물·유제품·가공식품·기타)를 쓰고, 키워드 매칭 시에만 개별 URL로 덮어씀. 허용 목록에 없는 분류 문자열은 `기타`로 정규화.

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

9. `templates/fridge.html` (검색·가상 결제 플로우)
   - 상단 폼: **추가** → **검색**, 유통기한은 `type="month"`(선택), 재료명·분류에 필수 표시(`*`).
   - 검색 시 가상 마트 상품 목록 모달. **유통기한 후보는 분류별 상한**(수산물·5일, 육류·7일, 채소·21일, 과일·35일, 유제품·28일, 가공식품·120일, 기타·60일)으로 오늘부터의 날짜만 사용. 연·월 선택 시 그 달과 위 범위의 **교집합**에서만 추출하고, 교집합이 비면 분류 범위만 사용.
   - **`type="month"` 입력**: 분류 확정 전에는 **비활성화**. 확정 후 `min`(이번 달)~`max`(오늘+분류별 최대일이 속한 달)를 설정해 브라우저 달력에서 범위 밖 달을 선택하지 못하게 함. 모달 상단은 재료명만, 각 행은 **유통기한·가격·수량**.
   - **가격 규칙(프론트 데모)**: 재료명 해시 **기본가 1,200~9,999원**. 임박 할인 배율의 기준 일수는 `max(14, 분류별 최대 보관일)`로 두어 유통이 짧은 분류에서도 가격 곡선이 덜 이질적으로 보이게 함(10원 단위 반올림).
   - 행마다 **유통기한 일자는 중복 없음**: 풀에서 시드 기반 Fisher–Yates 비복원 추출 후 **`expire_date` 오름차순** 정렬. `buildMockSearchRows`·`renderSearchResults`에서도 동일 기준 정렬.
   - **같은 검색 조건**(재료명·분류·연월)이면 **같은 날 안에서는** 항상 같은 행 개수·같은 유통기한·같은 가격 목록(시드 결정적). 자정이 지나 «오늘»이 바뀌면 유효일 풀이 달라져 결과가 바뀔 수 있음.
   - 체크박스·수량으로 복수 담기 후 **냉장고에 추가하기** → 총액 확인 모달 → **예** 시 가상 결제 완료 안내 후 기존 `/api/fridge/add`로 건별 저장.

10. `templates/fridge.html` (보관 목록 카드)
   - 동일 재료 그룹 **수량이 1개**일 때는 메인 그리드 카드에 분류 아래 **`~YYYY-MM-DD까지`** 형태로 유통기한을 표시. 2개 이상이면 기존처럼 임박 개수/신선 문구만 표시.

11. 재료명 검증·자동 분류 (`app/services/fridge_service.py`, `app/routes/fridge.py`, `templates/fridge.html`)
   - `FridgeService.validate_ingredient_name`: 형식(비어 있으면 **「재료명을 입력해주세요.」**, 1~40자·허용 문자 등) + **의미** 검사 — 가구·전자기기 등 `NONFOOD` 부분 문자열이면, 또는 알려진 식재료 키워드(분류 키워드 + `_EXTRA_FOOD_SUBSTRINGS`)가 하나도 없으면 **「올바른 재료명을 입력하세요」**. `add_ingredient` / `edit_ingredient`에서 동일.
   - `GET /api/fridge/infer-category?q=`: 비어 있으면 `기타`, 그 외는 위 검증 통과 시에만 분류 JSON 반환; 실패 시 400 + `message`.
   - 냉장고 검색 폼: **자동 분류** 또는 **직접 선택**(토글로 `select` 표시)으로만 분류 확정(`addFormCategoryConfirmed`). 재료명 변경 시 분류·확정 초기화. **검색**은 둘 중 하나로 분류를 정한 뒤에만 가능.
   - 분류 키워드: **쪽파·파·신파·실파·부추·미나리·열무·청경채** 등 채소 보강. **가공식품**을 채소보다 먼저 검사하고 **파스타·스파게티**를 넣어 `파` 단독 매칭과 구분. 클라이언트 `FOOD_SUBSTRINGS` 순서도 서버와 동일하게 유지.

12. 토스 결제창 (`app/routes/payment_toss.py`, `app/__init__.py`, `templates/fridge.html`)
   - **로그인 불필요**: `POST /payment/toss/prepare`로 장바구니·금액을 세션에 저장 후, 프론트에서 토스 SDK v2 `payment.requestPayment`(카드·리다이렉트) 호출.
   - **성공** `GET /payment/toss/success`: `orderId`·`amount` 세션 검증 후 `POST https://api.tosspayments.com/v1/payments/confirm`(Basic + 시크릿 키) 승인, 이어서 `FridgeService.add_ingredient` 반복. 저장 대상 사용자: `session['userID']`가 있으면 해당 사용자, 없으면 **`FRIDGE_PAYMENT_USER_ID`**(미설정 시 `1`).
   - **실패** `GET /payment/toss/fail`: 세션 정리 후 플래시·냉장고로 리다이렉트.
   - `.env`: **`TOSS_CLIENT_KEY`**(결제창용 **API 개별 연동** 클라이언트 키), **`TOSS_SECRET_KEY`**. 키 없으면 prepare는 503 안내.
