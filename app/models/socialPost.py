from datetime import datetime
from extensions import db


class SocialPost(db.Model):
    __tablename__ = "socialPosts"

    id = db.Column("ID", db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(
        "userID",
        db.Integer,
        db.ForeignKey("users.ID", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipeID = db.Column("recipeID", db.String(255), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    imagePath = db.Column("imagePath", db.String(255), nullable=False, default="")
    createdAt = db.Column("createdAt", db.DateTime, default=datetime.utcnow, nullable=False)
