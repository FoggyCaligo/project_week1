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
