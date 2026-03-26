from database import db
from sqlalchemy.sql import func

class SocialPost(db.Model):
    __tablename__ = 'socialPosts'

    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='게시글 ID')
    userID = db.Column(db.BigInteger, db.ForeignKey('users.ID'), nullable=False, comment='작성자 ID')
    recipeID = db.Column(db.String(255), comment='관련 레시피 ID')
    title = db.Column(db.String(255), nullable=False, comment='제목')
    content = db.Column(db.Text, nullable=False, comment='후기 내용')

    imagePath = db.Column(db.String(255), comment='업로드 이미지 경로')
    imageData = db.Column(db.LargeBinary, comment='업로드 이미지 바이너리')
    imageMimeType = db.Column(db.String(100), comment='이미지 MIME 타입')

    createdAt = db.Column(db.DateTime, server_default=func.current_timestamp(), comment='작성일')
    
class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='북마크 ID')
    userID = db.Column(db.BigInteger, db.ForeignKey('users.ID'), nullable=False, comment='사용자 ID')
    recipeID = db.Column(db.String(255), nullable=False, comment='레시피 ID')
    createdAt = db.Column(db.DateTime, server_default=func.current_timestamp(), comment='저장일')