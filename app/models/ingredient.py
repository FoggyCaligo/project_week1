from datetime import datetime
from extensions import db

class UserIngredient(db.Model):
    """
    사용자의 냉장고 재료를 관리하는 테이블 (팀원2 역할)
    """
    __tablename__ = 'user_ingredients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 팀원1의 users 테이블과 연동되는 외래키 (현재는 주석 처리, 병합 후 연결)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    ingredient_name = db.Column(db.String(120), nullable=False) 
    normalized_name = db.Column(db.String(120), nullable=False, index=True)  # API 매칭용 정규화 이름 (공백제거 등)
    category = db.Column(db.String(50), nullable=False)          # 육류, 채소류 등
    expire_date = db.Column(db.Date, nullable=False)             # 유통기한
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) # 등록일

    def __repr__(self):
        return f'<UserIngredient {self.ingredient_name}>'
    def to_dict(self):
        """API 응답용 딕셔너리 변환 메서드"""
        days_left = (self.expire_date - datetime.utcnow().date()).days
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ingredient_name': self.ingredient_name,
            'normalized_name': self.normalized_name,
            'category': self.category,
            'expire_date': self.expire_date.strftime('%Y-%m-%d'),
            'days_left': days_left,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }