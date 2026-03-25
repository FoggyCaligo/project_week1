from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nick_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    ingredients = db.relationship(
        "UserIngredient",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
    bookmarks = db.relationship(
        "Bookmark",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
    social_posts = db.relationship(
        "SocialPost",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )