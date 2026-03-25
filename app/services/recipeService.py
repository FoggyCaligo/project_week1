
from app.models.recipe import Recipe
from database import db
import re

class RecipeDetailService:
    def __init__(self):
        pass

    def get_formatted_recipe(self, recipe_id, user_id=None):
        from app.common import getOwnedIngredientSet, normalizeIngredientName

        # 데이터베이스에서 레시피 정보 조회
        recipe = db.session.get(Recipe, recipe_id)
        if not recipe:
            return None
        
        ownedIngredientSet = getOwnedIngredientSet(user_id)
        
        # 1. 재료 정보 파싱 및 보유 여부 확인
        detail_ingredients = []
        owned_count = 0
        if recipe.rcpPartsDtls:
            # 줄바꿈이나 쉼표로 구분된 재료 텍스트 파싱
            import re
            parts = re.split(r'[,|\n]', recipe.rcpPartsDtls)
            for part in parts:
                raw_name = part.strip()
                if not raw_name: continue
                
                # 재료명에서 양(amount) 분리 시도 (간단한 공백 기준)
                name_parts = raw_name.split(' ', 1)
                name_only = name_parts[0]
                amount = name_parts[1] if len(name_parts) > 1 else ""
                
                is_owned = normalizeIngredientName(name_only) in ownedIngredientSet
                if is_owned: owned_count += 1
                
                detail_ingredients.append({
                    "name": name_only,
                    "amount": amount,
                    "isOwned": is_owned
                })
        
        total_count = len(detail_ingredients)
        match_percent = round((owned_count / total_count) * 100) if total_count > 0 else 0

        # 2. 결과 딕셔너리 구성 (템플릿 필드명에 맞춤)
        formatted = {
            "recipeID": recipe.rcpSeq,
            "recipeName": recipe.rcpNm,
            "description": f"{recipe.rcpWay2} | {recipe.rcpPat2}",
            "cookTime": 15, # 기본값
            "calories": recipe.infoEng,
            "servingSize": 1, # 기본값
            "matchPercent": match_percent,
            "imageUrl": recipe.attFileNoMain,
            "ingredients": detail_ingredients,
            "nutrition": {
                "carbohydrate": recipe.infoCar,
                "protein": recipe.infoPro,
                "fat": recipe.infoFat,
            }
        }

        # 3. 요리 단계 구성
        steps = []
        for i in range(1, 21):
            idx = f"{i:02}"
            step_text = getattr(recipe, f"manual{idx}", None)
            step_img = getattr(recipe, f"manualImg{idx}", None)
            
            if step_text:
                cleaned_text = step_text.rstrip('abc\n\r ').strip()
                cleaned_text = re.sub(r'•[^:]*:', '', cleaned_text).strip()
                cleaned_text = re.sub(r'●[^:]*:', '', cleaned_text).strip()
                cleaned_text = re.sub(r'^\d+\.\s*', '', cleaned_text)
                steps.append({
                    "title": f"Step {i}",
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
