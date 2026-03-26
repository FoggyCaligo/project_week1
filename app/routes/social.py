from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from uuid import uuid4
from pathlib import Path

from app.common import (
    getCurrentUser,
    requireLogin,
    getNextID,
    getNow,
    socialPosts,
    bookmarks,
    findUserByID,
    getRecipeByID,
    formatDateTime,
)

social_bp = Blueprint("social", __name__)

def isAllowedImageFile(fileName: str) -> bool:
    allowedExtensions = {"png", "jpg", "jpeg", "gif", "webp"}
    return "." in fileName and fileName.rsplit(".", 1)[1].lower() in allowedExtensions
@social_bp.route("/social")
def socialPage():
    currentUser = getCurrentUser()

    availableRecipes = []

    if currentUser:
        userBookmarkList = sorted(
            [item for item in bookmarks if item["userID"] == currentUser["id"]],
            key=lambda item: item["createdAt"],
            reverse=True,
        )

        for bookmarkData in userBookmarkList:
            recipeData = getRecipeByID(bookmarkData["recipeID"])
            if recipeData:
                availableRecipes.append(
                    {
                        "recipeID": recipeData["recipeID"],
                        "recipeName": recipeData["recipeName"],
                    }
                )

    socialPostViewList = []
    for postData in sorted(socialPosts, key=lambda item: item["createdAt"], reverse=True):
        writerData = findUserByID(postData["userID"])
        recipeData = getRecipeByID(postData["recipeID"])

        socialPostViewList.append(
            {
                "id": postData["id"],
                "title": postData["title"],
                "content": postData["content"],
                "imagePath": postData["imagePath"],
                "createdAt": formatDateTime(postData["createdAt"]),
                "nickName": writerData["nickName"] if writerData else "알 수 없음",
                "recipeName": recipeData["recipeName"] if recipeData else "레시피 없음",
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
    currentUser, redirectResponse = requireLogin()
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

    isBookmarkedRecipe = any(
        item["userID"] == currentUser["id"] and item["recipeID"] == recipeID
        for item in bookmarks
    )

    if not isBookmarkedRecipe:
        flash("북마크한 레시피만 후기로 등록할 수 있습니다.", "error")
        return redirect(url_for("social.socialPage"))

    imagePath = ""

    if imageFile and imageFile.filename:
        safeFileName = secure_filename(imageFile.filename)

        if not isAllowedImageFile(safeFileName):
            flash("이미지 파일만 업로드할 수 있습니다. (png, jpg, jpeg, gif, webp)", "error")
            return redirect(url_for("social.socialPage"))

        savedName = f"{uuid4().hex}{Path(safeFileName).suffix.lower()}"
        savePath = Path(current_app.config["UPLOAD_FOLDER"]) / savedName
        imageFile.save(savePath)
        imagePath = f"/static/uploads/{savedName}"

    socialPosts.append(
        {
            "id": getNextID(socialPosts),
            "userID": currentUser["id"],
            "recipeID": recipeID,
            "title": title,
            "content": content,
            "imagePath": imagePath,
            "createdAt": getNow(),
        }
    )

    flash("후기가 등록되었습니다.", "success")
    return redirect(url_for("social.socialPage"))