from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from io import BytesIO
from werkzeug.utils import secure_filename
from uuid import uuid4
from pathlib import Path

from database import db
from app.common import getRecipeByID, formatDateTime
from app.services.authService import AuthService
from app.models.social import Bookmark, SocialPost

social_bp = Blueprint("social", __name__)

def isAllowedImageFile(fileName: str) -> bool:
    allowedExtensions = {"png", "jpg", "jpeg", "gif", "webp"}
    return "." in fileName and fileName.rsplit(".", 1)[1].lower() in allowedExtensions

@social_bp.route("/social")
def socialPage():
    currentUser = AuthService.getCurrentUser()

    availableRecipes = []

    if currentUser:
        userBookmarkList = (
            Bookmark.query
            .filter_by(userID=currentUser.ID)
            .order_by(Bookmark.createdAt.desc())
            .all()
        )

        for bookmarkData in userBookmarkList:
            recipeData = getRecipeByID(bookmarkData.recipeID)
            if recipeData:
                availableRecipes.append(
                    {
                        "recipeID": recipeData["recipeID"],
                        "recipeName": recipeData["recipeName"],
                    }
                )

    socialPostViewList = []
    postList = SocialPost.query.order_by(SocialPost.createdAt.desc()).all()

    for postData in postList:
        writerData = AuthService.findUserByID(postData.userID)
        recipeData = getRecipeByID(postData.recipeID)

        socialPostViewList.append(
            {
                "id": postData.ID,
                "title": postData.title,
                "content": postData.content,
                "createdAt": formatDateTime(postData.createdAt),
                "nickName": writerData.nickName if writerData else "알 수 없음",
                "recipeName": recipeData["recipeName"] if recipeData else "레시피 없음",
                "hasImage": bool(postData.imageData),
            }
        )
    return render_template(
        "social.html",
        availableRecipes=availableRecipes,
        socialPosts=socialPostViewList,
        currentUser=currentUser,
    )

@social_bp.route("/social/create", methods=["POST"])
def createSocialPost():
    currentUser, redirectResponse = AuthService.requireLogin()
    if redirectResponse:
        return redirectResponse

    recipeID = request.form.get("recipeID", "").strip()
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    imageFile = request.files.get("imageFile")

    if not recipeID or not title or not content:
        flash("레시피, 제목, 내용을 모두 입력해주세요.", "error")
        return redirect(url_for("social.socialPage"))

    recipeData = getRecipeByID(recipeID)
    if recipeData is None:
        flash("선택한 레시피를 찾을 수 없습니다.", "error")
        return redirect(url_for("social.socialPage"))

    isBookmarkedRecipe = Bookmark.query.filter_by(
        userID=currentUser.ID,
        recipeID=recipeID
    ).first()

    if not isBookmarkedRecipe:
        flash("북마크한 레시피만 후기로 등록할 수 있습니다.", "error")
        return redirect(url_for("social.socialPage"))

    imageData = None
    imageMimeType = None

    if imageFile and imageFile.filename:
        safeFileName = secure_filename(imageFile.filename)

        if not isAllowedImageFile(safeFileName):
            flash("이미지 파일만 업로드할 수 있습니다. (png, jpg, jpeg, gif, webp)", "error")
            return redirect(url_for("social.socialPage"))

        imageData = imageFile.read()
        imageMimeType = imageFile.mimetype

    newPost = SocialPost(
        userID=currentUser.ID,
        recipeID=recipeID,
        title=title,
        content=content,
        imageData=imageData,
        imageMimeType=imageMimeType,
    )
    db.session.add(newPost)
    db.session.commit()

    flash("후기가 등록되었습니다.", "success")
    return redirect(url_for("social.socialPage"))

@social_bp.route("/social/image/<int:postID>")
def socialImage(postID: int):
    post = SocialPost.query.get_or_404(postID)

    if not post.imageData:
        return "", 404

    return send_file(
        BytesIO(post.imageData),
        mimetype=post.imageMimeType or "image/jpeg"
    )