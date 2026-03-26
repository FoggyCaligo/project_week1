# import os
# from datetime import datetime
# from app.models.ingredient import UserIngredient
# # extensions 대신 새로 만든 통합 database 파일에서 db를 가져옵니다.
# from database import db

# class FridgeService:
#     @staticmethod
#     def get_user_ingredients(user_id):
#         """특정 사용자의 냉장고 재료 목록을 유통기한 임박 순으로 조회합니다."""
#         return UserIngredient.query.filter_by(user_id=user_id).order_by(UserIngredient.expire_date.asc()).all()

#     @staticmethod
#     def add_ingredient(user_id, ingredient_name, category, expire_date_str):
#         """냉장고에 새로운 재료를 추가합니다."""
#         if not ingredient_name or not expire_date_str:
#             return False, "재료명과 유통기한을 모두 입력해주세요."
            
#         try:
#             expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
#         except ValueError:
#             return False, "유통기한은 YYYY-MM-DD 형식이어야 합니다."

#         normalized_name = ingredient_name.lower().replace(" ", "")
#         if not category:
#             category = "기타"
            
#         # 팀원의 인메모리 인증으로 인해 DB users 테이블에 사용자가 없을 경우 외래키 에러 방지용 임시 생성 (db.py의 ensureUser 로직)
#         from sqlalchemy import text
#         try:
#             db.session.execute(
#                 text("INSERT IGNORE INTO users (ID, userName, passwordHash, nickName) VALUES (:id, :un, :pw, :nn)"),
#                 {"id": user_id, "un": f"user_{user_id}", "pw": "dummy_hash", "nn": f"User {user_id}"}
#             )
#             db.session.commit()
#         except Exception:
#             db.session.rollback()
        
#         new_item = UserIngredient(
#             user_id=user_id,
#             ingredient_name=ingredient_name,
#             normalized_name=normalized_name,
#             category=category,
#             expire_date=expire_date
#         )
        
#         try:
#             db.session.add(new_item)
#             db.session.commit()
#             return True, new_item
#         except Exception as e:
#             db.session.rollback()
#             return False, f"데이터베이스 저장 오류: {str(e)}"

#     @staticmethod
#     def edit_ingredient(user_id, ingredient_id, ingredient_name, category, expire_date_str):
#         """냉장고 재료 정보를 수정합니다."""
#         item = UserIngredient.query.filter_by(id=ingredient_id, user_id=user_id).first()
#         if not item:
#             return False, "해당 재료를 찾을 수 없습니다."
            
#         if not ingredient_name or not expire_date_str:
#             return False, "재료명과 유통기한을 모두 입력해주세요."
            
#         try:
#             expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
#         except ValueError:
#             return False, "유통기한은 YYYY-MM-DD 형식이어야 합니다."

#         item.ingredient_name = ingredient_name
#         item.normalized_name = ingredient_name.lower().replace(" ", "")
#         item.category = category if category else "기타"
#         item.expire_date = expire_date
        
#         try:
#             db.session.commit()
#             return True, item
#         except Exception as e:
#             db.session.rollback()
#             return False, f"데이터베이스 저장 오류: {str(e)}"

#     @staticmethod
#     def delete_ingredient(user_id, ingredient_id):
#         """냉장고에서 특정 재료를 삭제합니다."""
#         item = UserIngredient.query.filter_by(id=ingredient_id, user_id=user_id).first()
#         if not item:
#             return False, "해당 재료를 찾을 수 없거나 삭제 권한이 없습니다."
            
#         try:
#             db.session.delete(item)
#             db.session.commit()
#             return True, "삭제 완료"
#         except Exception as e:
#             db.session.rollback()
#             return False, f"데이터베이스 삭제 오류: {str(e)}"

#     @staticmethod
#     def get_recommended_recipes(user_id):
#         """
#         사용자의 냉장고 재료 중 유통기한이 임박한 재료를 기반으로
#         공공데이터 API(COOKRCP01)를 활용하여 추천 레시피를 가져옵니다.
#         """
#         # 1. 유통기한이 가장 임박한 재료 최대 2개 추출
#         items = UserIngredient.query.filter_by(user_id=user_id).order_by(UserIngredient.expire_date.asc()).limit(2).all()
        
#         if not items:
#             return []
            
#         # 재료명 추출 (예: '새우', '가지')
#         ingredient_names = [item.ingredient_name for item in items]
#         search_query = ",".join(ingredient_names)
        
#         # 2. 공공 API 호출
#         api_key = "3601fcadc33549809411"  # 발급받은 OpenAPI 인증키
#         url = f"https://openapi.foodsafetykorea.go.kr/api/{api_key}/COOKRCP01/json/1/3/RCP_PARTS_DTLS=\"{search_query}\""
        
#         import requests
#         try:
#             response = requests.get(url, timeout=5)
#             data = response.json()
            
#             if "COOKRCP01" in data and "row" in data["COOKRCP01"]:
#                 recipes = data["COOKRCP01"]["row"]
                
#                 # 프론트엔드에 전달하기 좋게 가공
#                 # 스네이크 있다고 뭐라하는거 나올 수 있는데 openapi 파라미터가 스네이크여서 그거 따라갔음.
#                 # 필요할 때 바꿈.
#                 recommended = []
#                 for r in recipes:
#                     recommended.append({
#                         "recipeID": r.get("RCP_SEQ"),
#                         "recipeName": r.get("RCP_NM"),
#                         "imageUrl": r.get("ATT_FILE_NO_MAIN"),
#                         "description": r.get("RCP_WAY2") + " | " + r.get("RCP_PAT2"),
#                     })
#                 return recommended
#             return []
#         except Exception as e:
#             print(f"API 호출 오류: {e}")
#             return []

import os
from datetime import datetime
from app.models.ingredient import UserIngredient
from database import db

class FridgeService:
    @staticmethod
    def get_user_ingredients(user_id):
        """특정 사용자의 냉장고 재료 목록을 유통기한 임박 순으로 조회합니다."""
        # user_id -> userID, expire_date -> expireDate
        return UserIngredient.query.filter_by(userID=user_id).order_by(UserIngredient.expireDate.asc()).all()

    @staticmethod
    def add_ingredient(user_id, ingredient_name, expire_date_str):
        """냉장고에 새로운 재료를 추가합니다."""
        if not ingredient_name or not expire_date_str:
            return False, "재료명과 유통기한을 모두 입력해주세요."
            
        try:
            expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
        except ValueError:
            return False, "유통기한은 YYYY-MM-DD 형식이어야 합니다."

        normalized_name = ingredient_name.lower().replace(" ", "")
            
        # 팀원의 인메모리 인증으로 인해 DB users 테이블에 사용자가 없을 경우 외래키 에러 방지용 임시 생성 (db.py의 ensureUser 로직)
        from sqlalchemy import text
        try:
            db.session.execute(
                text("INSERT IGNORE INTO users (ID, userName, passwordHash, nickName) VALUES (:id, :un, :pw, :nn)"),
                {"id": user_id, "un": f"user_{user_id}", "pw": "dummy_hash", "nn": f"User {user_id}"}
            )
            db.session.commit()
        except Exception:
            db.session.rollback()
        
        # 모델의 카멜 케이스 속성명에 맞게 매핑
        new_item = UserIngredient(
            userID=user_id,
            ingredientName=ingredient_name,
            normalizedName=normalized_name,
            expireDate=expire_date
        )
        
        try:
            db.session.add(new_item)
            db.session.commit()
            return True, new_item
        except Exception as e:
            db.session.rollback()
            return False, f"데이터베이스 저장 오류: {str(e)}"

    @staticmethod
    def edit_ingredient(user_id, ingredient_id, ingredient_name, expire_date_str):
        """냉장고 재료 정보를 수정합니다."""
        # id -> ID, user_id -> userID
        item = UserIngredient.query.filter_by(ID=ingredient_id, userID=user_id).first()
        if not item:
            return False, "해당 재료를 찾을 수 없습니다."
            
        if not ingredient_name or not expire_date_str:
            return False, "재료명과 유통기한을 모두 입력해주세요."
            
        try:
            expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
        except ValueError:
            return False, "유통기한은 YYYY-MM-DD 형식이어야 합니다."

        # 모델 속성 업데이트 (카멜 케이스)
        item.ingredientName = ingredient_name
        item.normalizedName = ingredient_name.lower().replace(" ", "")
        item.expireDate = expire_date
        
        try:
            db.session.commit()
            return True, item
        except Exception as e:
            db.session.rollback()
            return False, f"데이터베이스 저장 오류: {str(e)}"

    @staticmethod
    def delete_ingredient(user_id, ingredient_id):
        """냉장고에서 특정 재료를 삭제합니다."""
        # id -> ID, user_id -> userID
        item = UserIngredient.query.filter_by(ID=ingredient_id, userID=user_id).first()
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
        # 1. 유통기한이 가장 임박한 재료 최대 2개 추출 (user_id -> userID, expire_date -> expireDate)
        items = UserIngredient.query.filter_by(userID=user_id).order_by(UserIngredient.expireDate.asc()).limit(2).all()
        
        if not items:
            return []
            
        # 재료명 추출 (ingredient_name -> ingredientName)
        ingredient_names = [item.ingredientName for item in items]
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