# 냉장고 파트 고도화 (이미지 적용 및 버그 픽스)

다음 파일들이 냉장고 기능 고도화(재료별 사진 매핑) 및 500 에러 수정을 위해 수정되었습니다.

1. `app/routes/fridge_views.py`
   - 비로그인 상태에서 '/fridge' 진입 시 리다이렉트하는 코드를 기존 `loginPage`에서 새로운 블루프린트 구조인 `auth.login`으로 변경하여 500 에러 방지.

2. `app/models/ingredient.py`
   - `UserIngredient.to_dict()` 메서드를 확장하여 식재료 이름(`ingredientName`)에 해당하는 이미지를 매핑하여 `image_url` 필드로 반환하도록 구현.
   - 두부, 계란, 당근, 양파, 마늘 등 주요 식재료에 대해 무료 고화질 이미지(Unsplash) URL 매핑. (해당 없는 경우 기본 이미지 표시)

3. `templates/fridge.html`
   - 식재료 리스트 왼쪽의 동그란 아이콘을 삭제하고, 서버에서 받아온 `item.image_url`을 적용한 이미지 태그(`<img>`)로 교체.
   - 모달(상세보기 창) 상단에도 해당 재료의 이미지를 크고 둥글게(120x120) 표시하도록 레이아웃 추가.
   - CSS 스타일(object-fit: cover, border-radius)을 통해 이미지가 찌그러지지 않고 예쁘게 나오도록 조정.
