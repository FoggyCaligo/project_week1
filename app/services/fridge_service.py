import os
from datetime import datetime
from app.models.ingredient import UserIngredient
from app import db

class FridgeService:
    @staticmethod
    def get_user_ingredients(user_id):
        """특정 사용자의 냉장고 재료 목록을 유통기한 임박 순으로 조회합니다."""
        return UserIngredient.query.filter_by(user_id=user_id).order_by(UserIngredient.expire_date.asc()).all()

    @staticmethod
    def add_ingredient(user_id, ingredient_name, category, expire_date_str):
        """냉장고에 새로운 재료를 추가합니다."""
        if not ingredient_name or not expire_date_str:
            return False, "재료명과 유통기한을 모두 입력해주세요."
            
        try:
            expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
        except ValueError:
            return False, "유통기한은 YYYY-MM-DD 형식이어야 합니다."

        normalized_name = ingredient_name.lower().replace(" ", "")
        if not category:
            category = "기타"

        new_item = UserIngredient(
            user_id=user_id,
            ingredient_name=ingredient_name,
            normalized_name=normalized_name,
            category=category,
            expire_date=expire_date
        )
        
        try:
            db.session.add(new_item)
            db.session.commit()
            return True, new_item
        except Exception as e:
            db.session.rollback()
            return False, f"데이터베이스 저장 오류: {str(e)}"

    @staticmethod
    def delete_ingredient(user_id, ingredient_id):
        """냉장고에서 특정 재료를 삭제합니다."""
        item = UserIngredient.query.filter_by(id=ingredient_id, user_id=user_id).first()
        if not item:
            return False, "해당 재료를 찾을 수 없거나 삭제 권한이 없습니다."
            
        try:
            db.session.delete(item)
            db.session.commit()
            return True, "삭제 완료"
        except Exception as e:
            db.session.rollback()
            return False, f"데이터베이스 삭제 오류: {str(e)}"

    @staticmethod
    def get_recommended_recipes(user_id):
        """
        사용자의 냉장고 재료 중 유통기한이 임박한 재료를 기반으로
        공공데이터 API(COOKRCP01)를 활용하여 추천 레시피를 가져옵니다.
        """
        # 1. 유통기한이 가장 임박한 재료 최대 2개 추출
        items = UserIngredient.query.filter_by(user_id=user_id).order_by(UserIngredient.expire_date.asc()).limit(2).all()
        
        if not items:
            return []
            
        # 재료명 추출 (예: '새우', '가지')
        ingredient_names = [item.ingredient_name for item in items]
        search_query = ",".join(ingredient_names)
        
        # 2. 공공 API 호출
        api_key = "3601fcadc33549809411"  # 발급받은 OpenAPI 인증키
        url = f"https://openapi.foodsafetykorea.go.kr/api/{api_key}/COOKRCP01/json/1/3/RCP_PARTS_DTLS=\"{search_query}\""
        
        import requests
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if "COOKRCP01" in data and "row" in data["COOKRCP01"]:
                recipes = data["COOKRCP01"]["row"]
                
                # 프론트엔드에 전달하기 좋게 가공
                recommended = []
                for r in recipes:
                    recommended.append({
                        "recipeID": r.get("RCP_SEQ"),
                        "recipeName": r.get("RCP_NM"),
                        "imageUrl": r.get("ATT_FILE_NO_MAIN"),
                        "description": r.get("RCP_WAY2") + " | " + r.get("RCP_PAT2"),
                    })
                return recommended
            return []
        except Exception as e:
            print(f"API 호출 오류: {e}")
            return []

