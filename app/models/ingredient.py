from datetime import datetime

from extensions import db


class UserIngredient(db.Model):
    """
    사용자의 냉장고 재료를 관리하는 테이블 (팀원2 역할)
    """
    __tablename__ = "userIngredients"

    id = db.Column("ID", db.Integer, primary_key=True, autoincrement=True)
    # 팀원1의 users 테이블과 연동되는 외래키
    userID = db.Column(
        "userID",
        db.Integer,
        db.ForeignKey("users.ID", ondelete="CASCADE"),
        nullable=False,
    )
    ingredientName = db.Column("ingredientName", db.String(255), nullable=False)
    normalizedName = db.Column("normalizedName", db.String(255), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)
    expireDate = db.Column("expireDate", db.Date, nullable=False)
    createdAt = db.Column("createdAt", db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UserIngredient {self.ingredientName}>"

    def to_dict(self):
        """API 응답용 딕셔너리 변환 메서드"""
        daysLeft = (self.expireDate - datetime.utcnow().date()).days
        return {
            "id": self.id,
            "userID": self.userID,
            "ingredientName": self.ingredientName,
            "normalizedName": self.normalizedName,
            "category": self.category,
            "expireDate": self.expireDate.strftime("%Y-%m-%d"),
            "daysLeft": daysLeft,
            "createdAt": self.createdAt.strftime("%Y-%m-%d %H:%M:%S"),
        }
