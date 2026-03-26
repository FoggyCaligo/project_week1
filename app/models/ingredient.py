# from database import db
# from sqlalchemy.sql import func

# class UserIngredient(db.Model):
#     __tablename__ = 'userIngredients'

#     ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='식재료 레코드 ID')
#     userID = db.Column(db.BigInteger, db.ForeignKey('users.ID'), nullable=False, comment='사용자 ID')
#     ingredientName = db.Column(db.String(255), nullable=False, comment='입력 원본 재료명')
#     normalizedName = db.Column(db.String(255), comment='정규화된 재료명')
#     expireDate = db.Column(db.Date, comment='유통기한')
#     createdAt = db.Column(db.DateTime, server_default=func.current_timestamp(), comment='등록일')

# class IngredientAlias(db.Model):
#     __tablename__ = 'ingredientAlias'

#     ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='사전 ID')
#     aliasName = db.Column(db.String(255), nullable=False, comment='별칭 재료명')
#     standardName = db.Column(db.String(255), nullable=False, comment='표준 재료명')

from database import db
from sqlalchemy.sql import func

# 재료명 키워드 매칭 실패 시 분류별 공통 이미지 (FridgeService.ALLOWED_INGREDIENT_CATEGORIES 와 동일 키)
_IMG = "?q=80&w=200&h=200&auto=format&fit=crop"
CATEGORY_DEFAULT_IMAGES = {
    "채소": f"https://images.unsplash.com/photo-1540420773420-3366772f4999{_IMG}",
    "과일": f"https://images.unsplash.com/photo-1490818387583-1baba5e638af{_IMG}",
    "육류": f"https://images.unsplash.com/photo-1603048297172-c92544798d5e{_IMG}",
    "수산물": f"https://images.unsplash.com/photo-1519708227418-c8fd9a32b84a{_IMG}",
    "유제품": f"https://images.unsplash.com/photo-1550583724-b2692b85b150{_IMG}",
    "가공식품": f"https://images.unsplash.com/photo-1607623487719-385e9ce82f5a{_IMG}",
    "기타": f"https://images.unsplash.com/photo-1542838132-92c53300491e{_IMG}",
}


class UserIngredient(db.Model):
    __tablename__ = 'userIngredients'

    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='식재료 레코드 ID')
    userID = db.Column(db.BigInteger, db.ForeignKey('users.ID'), nullable=False, comment='사용자 ID')
    ingredientName = db.Column(db.String(255), nullable=False, comment='입력 원본 재료명')
    normalizedName = db.Column(db.String(255), comment='정규화된 재료명')
    expireDate = db.Column(db.Date, comment='유통기한')
    category = db.Column(db.String(32), nullable=True, comment='분류(채소/과일/육류 등)')
    createdAt = db.Column(db.DateTime, server_default=func.current_timestamp(), comment='등록일')

    def to_dict(self):
        """API 응답용 딕셔너리 변환 메서드 (프론트엔드 연동용)"""
        from datetime import date
        days_left = (self.expireDate - date.today()).days if self.expireDate else None
        
        # 이미지 매핑 로직 (키워드 부분 일치, 긴 키부터 검사해 '파'가 '파스타'에 먼저 걸리는 등 완화)
        image_map = {
            "두부": "https://images.unsplash.com/photo-1588600878108-578307a3cc9d?q=80&w=200&h=200&auto=format&fit=crop",
            "계란": "https://images.unsplash.com/photo-1587486913049-53fc88980cfc?q=80&w=200&h=200&auto=format&fit=crop",
            "달걀": "https://images.unsplash.com/photo-1587486913049-53fc88980cfc?q=80&w=200&h=200&auto=format&fit=crop",
            "당근": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?q=80&w=200&h=200&auto=format&fit=crop",
            "양파": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?q=80&w=200&h=200&auto=format&fit=crop",
            "마늘": "https://images.unsplash.com/photo-1540148426945-66205b5ce871?q=80&w=200&h=200&auto=format&fit=crop",
            "대파": "https://images.unsplash.com/photo-1592394533824-9440e5d68530?q=80&w=200&h=200&auto=format&fit=crop",
            "파": "https://images.unsplash.com/photo-1592394533824-9440e5d68530?q=80&w=200&h=200&auto=format&fit=crop",
            "감자": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?q=80&w=200&h=200&auto=format&fit=crop",
            "돼지고기": "https://images.unsplash.com/photo-1602491453631-e2a5ad90a131?q=80&w=200&h=200&auto=format&fit=crop",
            "소고기": "https://images.unsplash.com/photo-1603048297172-c92544798d5e?q=80&w=200&h=200&auto=format&fit=crop",
            "우유": "https://images.unsplash.com/photo-1550583724-b2692b85b150?q=80&w=200&h=200&auto=format&fit=crop",
            "김치": "https://images.unsplash.com/photo-1583224964978-225ddb3ea43f?q=80&w=200&h=200&auto=format&fit=crop",
            "간장": "https://images.unsplash.com/photo-1499126167718-c87f5c1387e8?q=80&w=200&h=200&auto=format&fit=crop",
            "사과": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?q=80&w=200&h=200&auto=format&fit=crop",
            "배": "https://images.unsplash.com/photo-1514756331096-242fdeb70d4a?q=80&w=200&h=200&auto=format&fit=crop",
            "바나나": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?q=80&w=200&h=200&auto=format&fit=crop",
            "토마토": "https://images.unsplash.com/photo-1546470427-e262649f7046?q=80&w=200&h=200&auto=format&fit=crop",
            "오이": "https://images.unsplash.com/photo-1604977042232-7f4e375e9b4b?q=80&w=200&h=200&auto=format&fit=crop",
        }

        category_normalized = (self.category or "").strip() or "기타"
        if category_normalized not in CATEGORY_DEFAULT_IMAGES:
            category_normalized = "기타"

        # 키워드 매칭 없으면 분류별 공통 이미지 → 알 수 없는 분류는 기타
        matched_image = CATEGORY_DEFAULT_IMAGES[category_normalized]
        if self.ingredientName:
            name = self.ingredientName
            for key, url in sorted(image_map.items(), key=lambda kv: len(kv[0]), reverse=True):
                if key in name:
                    matched_image = url
                    break

        return {
            'id': self.ID,
            'user_id': self.userID,
            'ingredient_name': self.ingredientName,
            'normalized_name': self.normalizedName,
            'expire_date': self.expireDate.strftime('%Y-%m-%d') if self.expireDate else "",
            'days_left': days_left,
            'created_at': self.createdAt.strftime('%Y-%m-%d %H:%M:%S') if self.createdAt else "",
            'image_url': matched_image,
            'category': category_normalized,
        }

class IngredientAlias(db.Model):
    __tablename__ = 'ingredientAlias'

    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='사전 ID')
    aliasName = db.Column(db.String(255), nullable=False, comment='별칭 재료명')
    standardName = db.Column(db.String(255), nullable=False, comment='표준 재료명')