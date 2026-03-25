from extensions import db
from datetime import datetime

class UserIngredient(db.Model):
    """
    사용자의 냉장고 재료를 관리하는 테이블 (팀원2 역할)
    """
    __tablename__ = 'userIngredients'

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True) # 기존 DB는 소문자 id로 확인됨. DESCRIBE 결과 참조
    user_id = db.Column('userId', db.Integer, nullable=False, default=1)  # 테스트용 임시 user_id
    ingredient_name = db.Column('ingredientName', db.String(120), nullable=False)
    normalized_name = db.Column('normalizedName', db.String(120), nullable=True)
    category = db.Column('category', db.String(50), nullable=False, default="기타") # 기존 DB에 category 컬럼 추가
    expire_date = db.Column('expireDate', db.Date, nullable=True)             # 유통기한
    created_at = db.Column('createdAt', db.DateTime, default=datetime.utcnow) # 등록일

    def __repr__(self):
        return f'<UserIngredient {self.ingredient_name}>'

    def to_dict(self):
        """API 응답용 딕셔너리 변환 메서드"""
        days_left = (self.expire_date - datetime.utcnow().date()).days if self.expire_date else None
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ingredient_name': self.ingredient_name,
            'normalized_name': self.normalized_name,
            'category': self.category,
            'expire_date': self.expire_date.strftime('%Y-%m-%d') if self.expire_date else "",
            'days_left': days_left,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ""
        }