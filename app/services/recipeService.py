
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
            # [1단계: 세척]
            clean_text = recipe.rcpPartsDtls.replace('<br>', '\n').replace('<br/>', '\n')
            clean_text = re.sub(r'<.*?>', '', clean_text)
            clean_text = re.sub(r'\d+인분\s*기준', '', clean_text).strip()
            clean_text = clean_text.replace('•', '').strip()

            # 🎯 [2단계: 정밀 분리] 괄호 안의 쉼표는 무시하고 자르기!
            # 정규표현식 설명: 괄호()가 닫히지 않은 상태의 쉼표는 건너뛰고, 바깥 쉼표나 줄바꿈(\n)만 잡습니다.
            parts = re.split(r',(?![^()]*\))|\n', clean_text)
            
            current_section = "주재료"
            
            for part in parts:
                raw_item = part.strip()
                if not raw_item: continue
                
                # 섹션 제목 찾기 로직 (기존 유지)
                section_match = re.search(r'[\[●]?([^\[\]●>:]+)[\]>:]', raw_item)
                if section_match:
                    current_section = section_match.group(1).strip()
                    raw_item = re.sub(r'^[\[●]?([^\[\]●>:]+)[\]>:]', '', raw_item).strip()
                    if not raw_item: continue

                # 🎯 [3단계: 이름과 분량의 완벽한 분리]
                # '누들 떡볶이 떡(20개, 130g)' -> 이름: '누들 떡볶이 떡', 분량: '(20개, 130g)'
                # 괄호가 시작되는 지점을 기준으로 나눕니다.
                if '(' in raw_item:
                    name_only, amount = raw_item.split('(', 1)
                    name_only = name_only.strip()
                    amount = '(' + amount.strip() # 다시 괄호를 씌워줌
                else:
                    # 숫자가 시작되는 지점 찾기 (괄호 없는 경우 대비)
                    match = re.search(r'([^\d]+)\s*(.*)', raw_item)
                    if match:
                        name_only = match.group(1).strip()
                        amount = match.group(2).strip()
                    else:
                        name_only = raw_item
                        amount = ""
                
                # 보유 여부 확인 및 추가
                is_owned = normalizeIngredientName(name_only) in ownedIngredientSet
                if is_owned: owned_count += 1
                
                detail_ingredients.append({
                    "section": current_section,
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

