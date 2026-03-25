"""
########################################################################################
# 파일명: recipeDetailService.py
# 목적: 원본 데이터베이스 정보(Repository)와 웹 인터페이스(Flask) 사이를 연결하며, 
#       복잡한 컬럼 정보를 보기 좋게 가공하여 전달하는 서비스 레이어입니다.
# 
# 입력:   recipe_id (int) - 조회를 원하는 RCP_SEQ 숫자.
# 출력:   - rcpName, imageUrl: 가독성 있는 키 명칭으로 변경된 정보.
#         - steps: 20단계의 매뉴얼을 리스트 형태로 묶어서 반환.
#         - nutrition: 칼로리, 탄단지 정보가 정리된 객체.
#
# 사용 방법:
#   from db import Database
#   from repository.recipeDetailRepository import RecipeDetailRepository
#   from service.recipeDetailService import RecipeDetailService
#
#   db = Database()
#   repo = RecipeDetailRepository(db)
#   service = RecipeDetailService(repo)
#   
#   recipe_json = service.get_formatted_recipe(18)
########################################################################################
"""

import re

class RecipeDetailService:
    def __init__(self, repository):
        """
        repository: An instance of RecipeDetailRepository
        """
        self.repository = repository

    def get_formatted_recipe(self, recipe_id):
        raw_data = self.repository.get_recipe_details(recipe_id)
        
        if not raw_data:
            return None
        
        # 1. Base Information
        formatted = {
            "recipeID": raw_data.get("RCP_SEQ"),
            "recipeName": raw_data.get("RCP_NM"),
            "method": raw_data.get("RCP_WAY2"),
            "category": raw_data.get("RCP_PAT2"),
            "imageUrl": raw_data.get("ATT_FILE_NO_MAIN"),
            "ingredientsText": raw_data.get("RCP_PARTS_DTLS"),
            "nutrition": {
                "calories": raw_data.get("INFO_ENG"),
                "carbohydrate": raw_data.get("INFO_CAR"),
                "protein": raw_data.get("INFO_PRO"),
                "fat": raw_data.get("INFO_FAT"),
                "sodium": raw_data.get("INFO_NA")
            }
        }

        # 2. Extract Steps and Images dynamically (MANUAL01 - MANUAL20)
        steps = []
        for i in range(1, 21):  # The table has up to 20 steps
            step_num = f"{i:02}"  # Format as 01, 02...
            text_key = f"MANUAL{step_num}"
            img_key = f"MANUAL_IMG{step_num}"
            
            step_text = raw_data.get(text_key)
            step_img = raw_data.get(img_key)
            
            # Only add if the text for the step exists
            if step_text:
                # Clean up trailing characters like 'a', 'b', 'c' often found in this dataset
                cleaned_text = step_text.rstrip('abc\n\r ').strip()
                
                # Remove leading numbers (like "1. ", "2. ") from the database text
                # to avoid double-numbering since our template adds its own numbers.
                cleaned_text = re.sub(r'^\d+\.\s*', '', cleaned_text)
                
                steps.append({
                    "stepNumber": i,
                    "description": cleaned_text,
                    "imageUrl": step_img if step_img else ""
                })
        
        formatted["steps"] = steps
        
        return formatted

    def get_recipe_list(self, limit=10):
        """Fetches and formats multiple recipes for list views (like home or search)."""
        raw_list = self.repository.get_all_recipes(limit=limit)
        
        formatted_list = []
        for raw_data in raw_list:
            formatted_list.append({
                "recipeID": raw_data.get("RCP_SEQ"),
                "recipeName": raw_data.get("RCP_NM"),
                "imageUrl": raw_data.get("ATT_FILE_NO_MAIN"),
                "description": raw_data.get("RCP_WAY2") + " | " + raw_data.get("RCP_PAT2"),
                "cookTime": 15, # Constant for list view
                "matchPercent": 100 # Default since we're just listing
            })
        
        return formatted_list
