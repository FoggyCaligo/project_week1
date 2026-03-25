"""
########################################################################################
# 파일명: recipeDetailService.py
# 목적: SQLAlchemy ORM 모델(Recipe)과 웹 인터페이스(Flask) 사이를 연결하며, 
#       복잡한 컬럼 정보를 보기 좋게 가공하여 전달하는 서비스 레이어입니다.
# 
# 입력:   recipe_id (int) - 조회를 원하는 레시피의 기본키(RCP_SEQ).
#         limit (int)     - 조회할 레시피의 최대 개수 (기본값 10).
# 출력:   - rcpName, imageUrl 등의 데이터가 가독성 있는 키 명칭의 dict로 반환됩니다.
#         - steps: 최대 20단계의 순서와 사진이 포함된 리스트 반환.
#         - nutrition: 레시피의 영양소(칼로리, 탄단지 등)가 정리된 객체.
#
# 사용 방법:
#   from app.services.recipeDetailService import RecipeDetailService
#
#   service = RecipeDetailService()
#   recipe_json = service.get_formatted_recipe(18)
#
# 발생 가능한 오류 및 예외 처리:
#   - AttributeError: SQLAlchemy 객체에 존재하지 않는 컬럼 접근 시 발생 (getattr 사용)
#   - DB 연결 예외: 데이터베이스 서버가 꺼져있을 경우 sqlalchemy 관련 오류 발생
########################################################################################
"""
from app.models.foodRecipes import Recipe
from app import db
import re

class RecipeDetailService:
    def __init__(self):
        pass

    def get_formatted_recipe(self, recipe_id):
        # 데이터베이스에서 레시피 정보 조회
        recipe = db.session.get(Recipe, recipe_id)
        
        if not recipe:
            return None
        
        # 1. 기본 정보 정제
        formatted = {
            "recipeID": recipe.rcpSeq,
            "recipeName": recipe.rcpNm,
            "method": recipe.rcpWay2,
            "category": recipe.rcpPat2,
            "imageUrl": recipe.attFileNoMain,
            "ingredientsText": recipe.rcpPartsDtls,
            "nutrition": {
                "calories": recipe.infoEng,
                "carbohydrate": recipe.infoCar,
                "protein": recipe.infoPro,
                "fat": recipe.infoFat,
                "sodium": recipe.infoNa
            }
        }

        # 2. 요리 단계 및 이미지 추출
        steps = []
        for i in range(1, 21):  # 테이블에는 최대 20개의 순서가 존재
            num = f"{i:02}"
            step_text = getattr(recipe, f"manual{num}", None)
            step_img = getattr(recipe, f"manualImg{num}", None)
            
            # 단계 텍스트가 있을 경우에만 리스트에 추가
            if step_text:
                # 데이터셋에서 자주 보이는 끝부분 문자('a', 'b', 'c' 및 줄바꿈 등) 제거
                cleaned_text = step_text.rstrip('abc\n\r ').strip()
                
                # HTML 템플릿의 자체 넘버링과 겹치지 않게 숫자('1. ', '2. ' 등) 제거
                cleaned_text = re.sub(r'^\d+\.\s*', '', cleaned_text)
                
                steps.append({
                    "stepNumber": i,
                    "description": cleaned_text,
                    "imageUrl": step_img if step_img else ""
                })
        
        formatted["steps"] = steps
        
        return formatted

    def get_recipe_list(self, limit=10):
        """리스트 화면(홈 또는 검색 결과)에서 사용할 여러 레시피를 조회 후 정제합니다."""
        recipes = Recipe.query.limit(limit).all()
        
        formatted_list = []
        for recipe in recipes:
            formatted_list.append({
                "recipeID": recipe.rcpSeq,
                "recipeName": recipe.rcpNm,
                "imageUrl": recipe.attFileNoMain,
                "description": recipe.rcpWay2 + " | " + recipe.rcpPat2,
                "cookTime": 15, # 리스트 출력용 임의의 조리 시간(상수)
                "matchPercent": 100 # 순차 나열을 위한 임의 일치율(상수)
            })
        
        return formatted_list
