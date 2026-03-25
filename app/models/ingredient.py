from datetime import datetime
from app import db

class UserIngredient(db.Model):
    __tablename__ = 'user_ingredients'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False, default=1) # 1 for now
    ingredient_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False, default="기타")
    expire_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        days_left = (self.expire_date - datetime.utcnow().date()).days
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ingredient_name': self.ingredient_name,
            'category': self.category,
            'expire_date': self.expire_date.strftime('%Y-%m-%d'),
            'days_left': days_left,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
