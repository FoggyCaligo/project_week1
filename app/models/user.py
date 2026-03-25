from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column("ID", db.Integer, primary_key=True, autoincrement=True)
    userName = db.Column("userName", db.String(255), unique=True, nullable=False, index=True)
    passwordHash = db.Column("passwordHash", db.String(255), nullable=False)
    nickName = db.Column("nickName", db.String(255), nullable=False)
    createdAt = db.Column("createdAt", db.DateTime, default=datetime.utcnow, nullable=False)

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
    socialPosts = db.relationship(
        "SocialPost",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
