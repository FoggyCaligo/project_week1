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
        
        # 이미지 매핑 로직 (단순 구현)
        image_map = {
            "두부": "https://images.unsplash.com/photo-1588600878108-578307a3cc9d?q=80&w=200&h=200&auto=format&fit=crop",
            "계란": "https://images.unsplash.com/photo-1587486913049-53fc88980cfc?q=80&w=200&h=200&auto=format&fit=crop",
            "달걀": "https://images.unsplash.com/photo-1587486913049-53fc88980cfc?q=80&w=200&h=200&auto=format&fit=crop",
            "당근": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?q=80&w=200&h=200&auto=format&fit=crop",
            "양파": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?q=80&w=200&h=200&auto=format&fit=crop",
            "마늘": "https://images.unsplash.com/photo-1540148426945-66205b5ce871?q=80&w=200&h=200&auto=format&fit=crop",
            "파": "https://images.unsplash.com/photo-1592394533824-9440e5d68530?q=80&w=200&h=200&auto=format&fit=crop",
            "대파": "https://images.unsplash.com/photo-1592394533824-9440e5d68530?q=80&w=200&h=200&auto=format&fit=crop",
            "감자": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?q=80&w=200&h=200&auto=format&fit=crop",
            "돼지고기": "https://images.unsplash.com/photo-1602491453631-e2a5ad90a131?q=80&w=200&h=200&auto=format&fit=crop",
            "소고기": "https://images.unsplash.com/photo-1603048297172-c92544798d5e?q=80&w=200&h=200&auto=format&fit=crop",
            "우유": "https://images.unsplash.com/photo-1550583724-b2692b85b150?q=80&w=200&h=200&auto=format&fit=crop",
            "김치": "https://images.unsplash.com/photo-1583224964978-225ddb3ea43f?q=80&w=200&h=200&auto=format&fit=crop"
        }
        
        default_image = "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?q=80&w=200&h=200&auto=format&fit=crop"
        
        # 키워드 포함 검사로 매핑 (예: "햇양파" -> "양파" 이미지 매칭)
        matched_image = default_image
        if self.ingredientName:
            for key, url in image_map.items():
                if key in self.ingredientName:
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
            'category': (self.category or '').strip() or '기타',
        }

class IngredientAlias(db.Model):
    __tablename__ = 'ingredientAlias'

    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='사전 ID')
    aliasName = db.Column(db.String(255), nullable=False, comment='별칭 재료명')
    standardName = db.Column(db.String(255), nullable=False, comment='표준 재료명')