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
    createdAt = db.Column(db.DateTime, server_default=func.current_timestamp(), comment='등록일')

    def to_dict(self):
        """API 응답용 딕셔너리 변환 메서드 (프론트엔드 연동용)"""
        from datetime import date
        days_left = (self.expireDate - date.today()).days if self.expireDate else None
        return {
            'id': self.ID,
            'user_id': self.userID,
            'ingredient_name': self.ingredientName,
            'normalized_name': self.normalizedName,
            'expire_date': self.expireDate.strftime('%Y-%m-%d') if self.expireDate else "",
            'days_left': days_left,
            'created_at': self.createdAt.strftime('%Y-%m-%d %H:%M:%S') if self.createdAt else ""
        }

class IngredientAlias(db.Model):
    __tablename__ = 'ingredientAlias'

    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='사전 ID')
    aliasName = db.Column(db.String(255), nullable=False, comment='별칭 재료명')
    standardName = db.Column(db.String(255), nullable=False, comment='표준 재료명')