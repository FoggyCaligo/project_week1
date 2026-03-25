# 냉장고 파트 고도화 (이미지 적용 및 버그 픽스)

다음 파일들이 냉장고 기능 고도화(재료별 사진 매핑) 및 500 에러 수정을 위해 수정되었습니다.

1. `app/routes/fridge_views.py`
   - 비로그인 상태에서 '/fridge' 진입 시 리다이렉트하는 코드를 기존 `loginPage`에서 새로운 블루프린트 구조인 `auth.login`으로 변경하여 500 에러 방지.

2. `app/models/ingredient.py`
   - `UserIngredient.to_dict()` 메서드를 확장하여 식재료 이름(`ingredientName`)에 해당하는 이미지를 매핑하여 `image_url` 필드로 반환하도록 구현.
   - 두부, 계란, 당근, 양파, 마늘 등 주요 식재료에 대해 무료 고화질 이미지(Unsplash) URL 매핑. (해당 없는 경우 기본 이미지 표시)

5. `templates/fridge.html` (UI/UX 전체 고도화)
   - 동일한 이름을 가진 식재료들을 목록에서 각각 나열하지 않고 **그룹화(수량 표기)**하여 보여주도록 개선했습니다.
   - 식재료 목록 레이아웃을 기존 세로 리스트형에서 실제 냉장고처럼 보이는 **그리드(Grid)형 카드 레이아웃**으로 디자인을 전면 개편했습니다.
   - 특정 식재료(예: 당근) 카드를 클릭하면 나타나는 모달 창에서 **보관 중인 모든 항목의 수량, 유통기한, 등록일**을 개별적으로 확인하고 [수정/삭제]할 수 있도록 상세 뷰 UX를 최신 웹서비스에 맞게 고도화했습니다.

4. `app/services/fridge_service.py`
   - 식재료 추가(`add_ingredient`), 수정(`edit_ingredient`), 삭제(`delete_ingredient`) 시 `SQLAlchemy` ORM 객체의 외래키 바인딩 에러를 방지하기 위해 `원시 SQL(Raw SQL)`을 사용하도록 로직을 변경하여 500 에러 및 400 에러를 수정했습니다.
