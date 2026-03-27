# import re

# def clean_ingredient_name(raw_text):
#     text = re.sub(r'\(.*?\)', '', raw_text)
    
#     text = re.sub(r'[\d\./]+[gml|개|봉지|큰술|작은술|컵|가닥|cm|장|마리|쪽|알]*', '', text)
    
#     text = re.sub(r'[●:,\s]', '', text)
    
#     return text.strip()

# samples = [
#     "오이 70g(1/3개)",
#     "다진 땅콩 10g(1큰술)",
#     "북어채 25g(15개)",
#     "새우 10g(3마리)",
#     "무 30g(5×3×2cm)",
#     "대파 10g(5cm)"
# ]

# for s in samples:
#     print(f"[{s}] -> 결과: {clean_ingredient_name(s)}")

import random
import re
import requests
from app.models.recipe import Recipe
from sqlalchemy import func, cast, Float

class ApiService:
    
    @staticmethod
    def getRandomRecommendations(count=3):
        try:
            # 1. DB에서 랜덤하게 count개만큼 쿼리 (ORDER BY RAND())
            random_recipes = Recipe.query.order_by(func.rand()).limit(count).all()
            
            # 2. 템플릿에서 쓰기 편하게 리스트로 가공
            refined_list = []
            for r in random_recipes:
                refined_list.append({
                    "recipeID": r.rcpSeq,          # 모델의 PK 필드명에 맞게 수정
                    "RCP_NM": r.rcpNm, # 모델 필드명 확인
                    "ATT_FILE_NO_MAIN": r.attFileNoMain or "/static/images/default_recipe.jpg",
                    "RCP_PAT2": r.rcpPat2,
                    "description": f"{r.rcpWay2} | {r.rcpPat2}",
                    # 🎯 [추가] 비로그인/랜덤 추천 시 에러 방지용 빈 리스트
                    "haveIngredients": [],
                    "missingIngredients": [],
                    "matchPercent": 0
                })
            return refined_list
            
        except Exception as e:
            print(f"[DB Error] 랜덤 추천 실패: {e}")
            return []
    API_KEY = "sample"
    BASE_URL = f"http://openapi.foodsafetykorea.go.kr/api/{API_KEY}/COOKRCP01/json"
    @staticmethod
    def searchRecipesFromAPI(keyword, user_id=None, page=1, per_page=10):
        """
        [로그인 추천 검색용]
        기존 공공 API 검색 대신, 전체 레시피 검색과 동일한 DB(foodRecipes)를 조회한 뒤
        사용자 냉장고 재료 + 검색창 입력 재료를 기준으로 일치율을 다시 계산합니다.

        ※ 함수명은 기존 라우트/호출부 호환성을 위해 그대로 유지합니다.
        """
        if not keyword:
            return [], 0

        from app.models.ingredient import UserIngredient
        from app.services.fridge_service import FridgeService

        exclude_ingredients = {
            "기준", "재료", "주재료", "부재료", "양념", "소스", "고명", "선택", "준비", "약간",
            "인분", "인분기준", "내용물", "함량", "구성", "추가", "가정간편식",
            "소금", "설탕", "후추", "후춧가루", "고춧가루", "밀가루", "녹말가루", "전분",
            "식용유", "참기름", "들기름", "올리브유", "간장", "진간장", "국간장", "저염간장",
            "다진마늘", "마늘", "생강", "맛술", "청주", "물", "육수", "통깨", "깨",
            "올리고당", "물엿", "식초", "케찹", "마요네즈", "고추장", "된장"
        }

        try:
            keywords = [k.strip() for k in re.split(r'[\s,]+', keyword) if k.strip()]
            if not keywords:
                return [], 0

            owned_standard_set = set()
            if user_id is not None:
                owned_items = UserIngredient.query.filter_by(userID=user_id).all()
                owned_standard_set = {
                    FridgeService.get_standard_name(item.ingredientName)
                    for item in owned_items
                    if item.ingredientName
                }

            input_standard_set = {FridgeService.get_standard_name(name) for name in keywords}
            effective_owned_set = owned_standard_set | input_standard_set

            query = Recipe.query
            for k in keywords:
                search_term = f"%{k}%"
                query = query.filter(Recipe.rcpPartsDtls.like(search_term))

            pagination = query.order_by(Recipe.rcpSeq.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False,
            )

            refined_list = []
            for recipe in pagination.items:
                raw_parts = recipe.rcpPartsDtls or ""
                cleaned_full_text = FridgeService.clean_ingredient_name(raw_parts)
                parts_list = re.split(r'[\s,]+', cleaned_full_text)

                have_ingr = []
                missing_ingr = []

                for part in parts_list:
                    p_clean = part.strip()
                    if not p_clean or len(p_clean) < 2 or p_clean in exclude_ingredients:
                        continue

                    recipe_std_name = FridgeService.get_standard_name(p_clean)
                    if recipe_std_name in exclude_ingredients:
                        continue

                    if recipe_std_name in effective_owned_set:
                        if p_clean not in have_ingr:
                            have_ingr.append(p_clean)
                    else:
                        if p_clean not in missing_ingr:
                            missing_ingr.append(p_clean)

                total = len(have_ingr) + len(missing_ingr)
                match_percent = round((len(have_ingr) / total) * 100) if total > 0 else 0

                refined_list.append({
                    "recipeID": recipe.rcpSeq,
                    "RCP_NM": recipe.rcpNm,
                    "recipeName": recipe.rcpNm,
                    "ATT_FILE_NO_MAIN": recipe.attFileNoMain or "/static/images/default_recipe.jpg",
                    "imageUrl": recipe.attFileNoMain or "/static/images/default_recipe.jpg",
                    "RCP_PAT2": recipe.rcpPat2 or "요리",
                    "description": f"{recipe.rcpWay2 or '기타'} | {recipe.rcpPat2 or '요리'}",
                    "cookTime": 20,
                    "haveIngredients": have_ingr,
                    "missingIngredients": missing_ingr,
                    "matchPercent": match_percent,
                })

            return refined_list, pagination.pages or 1

        except Exception as e:
            print(f"[DB Recommend Search Error]: {e}")
            return [], 1

    @staticmethod
    def getAllRecipesWithPagination(page=1, per_page=12, sort='latest'):
        """
        [비회원/전체용] DB에서 전체 레시피를 페이징하여 가져옵니다.
        """
        try:
            # 🎯 [1단계: 주문에 맞춰 칼 갈기] 정렬 기준 설정
            if sort == 'name':
                # 이름 가나다순 (오름차순)
                order_criteria = Recipe.rcpNm.asc()
            elif sort == 'low_cal':
                # 데이터에 cookTime이 없으니 칼로리(infoEng) 낮은 순으로 센스 있게!
                # (만약 진짜 조리시간 컬럼이 있다면 그걸 쓰시면 됩니다)
                order_criteria = cast(Recipe.infoEng,Float).asc()
            else:
                # 기본값: 최신순 (ID 역순)
                order_criteria = Recipe.rcpSeq.desc()

            # 🎯 [2단계: 정렬된 쿼리로 페이징]
            pagination = Recipe.query.order_by(order_criteria).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # 3. 템플릿 규격에 맞게 가공 (기존 로직 유지)
            refined_recipes = []
            for r in pagination.items:
                refined_recipes.append({
                    "recipeID": r.rcpSeq,
                    "recipeName": r.rcpNm,
                    "imageUrl": r.attFileNoMain or "/static/images/default_recipe.jpg",
                    "category": r.rcpPat2 or "일반",
                    "parts_dtls": r.rcpPartsDtls or "",
                })
            
            return refined_recipes, pagination
            
        except Exception as e:
            print(f"[DB Error] 전체 레시피 로드 실패: {e}")
            return [], None
    @staticmethod
    def searchRecipesFromDB(keyword, page=1, per_page=12, sort='lastest'):
        """
        [비회원/전체용] 우리 DB에서 재료명으로 레시피를 검색합니다.
        """
        try:
            # 1. rcpPartsDtls(재료상세) 컬럼에 키워드가 포함된 것 찾기
            keywords = [k.strip() for k in keyword.replace(',', ' ').split() if k.strip()]
        
            query = Recipe.query
            
            # 2. 모든 키워드가 포함된 레시피만 필터링 (AND 조건)
            for k in keywords:
                search_term = f"%{k}%"
                query = query.filter(Recipe.rcpPartsDtls.like(search_term))
            if sort == 'name':
                order_criteria = Recipe.rcpNm.asc()
            elif sort == 'low_cal':
                order_criteria = Recipe.infoEng.asc() # 칼로리 낮은 순 등으로 대체
            else:
                order_criteria = Recipe.rcpSeq.desc() # 최신순
            pagination = query.order_by(order_criteria).paginate(
                page=page, per_page=per_page, error_out=False
            )

            # 2. 전체 레시피 페이지(all_recipes.html) 규격에 맞게 가공
            refined_recipes = []
            for r in pagination.items:
                refined_recipes.append({
                    "recipeID": r.rcpSeq,
                    "recipeName": r.rcpNm,
                    "imageUrl": r.attFileNoMain or "/static/images/default_recipe.jpg",
                    "category": r.rcpPat2 or "일반",
                    "parts_dtls": r.rcpPartsDtls or "", # 재료 미리보기용
                    "cookTime": 20
                })
            
            return refined_recipes, pagination
        except Exception as e:
            print(f"[DB Search Error]: {e}")
            return [], None