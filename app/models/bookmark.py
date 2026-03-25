from datetime import datetime
from extensions import db


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column("ID", db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(
        "userID",
        db.Integer,
        db.ForeignKey("users.ID", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipeID = db.Column("recipeID", db.String(255), nullable=False, index=True)
    createdAt = db.Column("createdAt", db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("userID", "recipeID", name="uq_bookmark_user_recipe"),
    )
