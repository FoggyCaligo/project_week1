# 냉장고 파트 고도화 (이미지 적용 및 버그 픽스)

다음 파일들이 냉장고 기능 고도화(재료별 사진 매핑) 및 500 에러 수정을 위해 수정되었습니다.

1. `app/routes/fridge_views.py`
   - 비로그인 상태에서 '/fridge' 진입 시 리다이렉트하는 코드를 기존 `loginPage`에서 새로운 블루프린트 구조인 `auth.login`으로 변경하여 500 에러 방지.

2. `app/models/ingredient.py`
   - `UserIngredient.to_dict()` 메서드를 확장하여 식재료 이름(`ingredientName`)에 해당하는 이미지를 매핑하여 `image_url` 필드로 반환하도록 구현.
   - 두부, 계란, 당근, 양파, 마늘 등 주요 식재료에 대해 무료 고화질 이미지(Unsplash) URL 매핑. (해당 없는 경우 기본 이미지 표시)

6. `templates/fridge.html` (동일 식재료 그룹 뱃지 고도화)
   - 그룹화된 식재료 카드에서 표시되는 유통기한 정보를 개선했습니다. 
   - 동일한 식재료 중 유통기한이 '임박(3일 이내)'이거나 '경과'한 항목이 있다면, 해당 카드에 "유통기한 임박: N개"라는 직관적인 경고 뱃지를 띄우도록 수정했습니다.
   - 모두 안전한 상태라면 "신선 보관중" 뱃지가 뜨도록 개선하여, 온라인 냉장고 관리 목적에 더욱 부합하도록 로직을 변경했습니다.

4. `app/services/fridge_service.py`
   - 식재료 추가(`add_ingredient`), 수정(`edit_ingredient`), 삭제(`delete_ingredient`) 시 `SQLAlchemy` ORM 객체의 외래키 바인딩 에러를 방지하기 위해 `원시 SQL(Raw SQL)`을 사용하도록 로직을 변경하여 500 에러 및 400 에러를 수정했습니다.
