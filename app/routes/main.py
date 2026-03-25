# 홈페이지('/')와 잡다한 라우트들(검색, 소셜 등)을 담당하는 메인 블루프린트 파일
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from uuid import uuid4
from pathlib import Path
from app.common import (
    getCurrentUser, buildHomeSummary, buildRecommendedRecipeList, getUserIngredientList,
    requireLogin, getRecipeByID, getNextID, getNow, bookmarks, socialPosts, findUserByID, buildRecipeCard, formatDateTime, buildRecipeDetail, recipeCatalog
)

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    currentUser = getCurrentUser()
    if currentUser:
        summary = buildHomeSummary(currentUser["id"])
        todayRecipes = buildRecommendedRecipeList(currentUser["id"])[:3]
        expiringIngredients = getUserIngredientList(currentUser["id"])[:5]
    else:
        summary = {"ingredientCount": 0, "expiringCount": 0, "recommendCount": 0}
        todayRecipes = buildRecommendedRecipeList(None, sortKey="cookTime")[:3]
        expiringIngredients = []

    return render_template("home.html", summary=summary, todayRecipes=todayRecipes, expiringIngredients=expiringIngredients)

@main_bp.route("/search")
def searchPage():
    currentUser = getCurrentUser()
    searchKeyword = request.args.get("q", "").strip()
    userID = currentUser["id"] if currentUser else None
    recipes = buildRecommendedRecipeList(userID=userID, sortKey="matchPercent", searchKeyword=searchKeyword)
    return render_template("recommend.html", recipes=recipes)

@main_bp.route("/recipes/recommend")
def recommendPage():
    currentUser = getCurrentUser()
    sortKey = request.args.get("sort", "matchPercent")
    userID = currentUser["id"] if currentUser else None
    recipes = buildRecommendedRecipeList(userID=userID, sortKey=sortKey)
    return render_template("recommend.html", recipes=recipes)

@main_bp.route("/recipes/<recipeID>")
def recipeDetailPage(recipeID: str):
    currentUser = getCurrentUser()
    userID = currentUser["id"] if currentUser else None
    recipe = buildRecipeDetail(recipeID, userID)
    if recipe is None:
        flash("레시피를 찾지 못했습니다.", "error")
        return redirect(url_for("main.recommendPage"))
    return render_template("recipe_detail.html", recipe=recipe)

@main_bp.route("/bookmarks/add/<recipeID>", methods=["POST"])
def addBookmark(recipeID: str):
    currentUser, redirectResponse = requireLogin()
    if redirectResponse: return redirectResponse
    recipeData = getRecipeByID(recipeID)
    if recipeData is None:
        flash("북마크할 레시피를 찾지 못했습니다.", "error")
        return redirect(url_for("main.recommendPage"))
    
    if next((item for item in bookmarks if item["userID"] == currentUser["id"] and item["recipeID"] == recipeID), None):
        flash("이미 북마크한 레시피입니다.", "info")
        return redirect(url_for("main.bookmarksPage"))

    bookmarks.append({"id": getNextID(bookmarks), "userID": currentUser["id"], "recipeID": recipeID, "createdAt": getNow()})
    flash("북마크에 저장되었습니다.", "success")
    return redirect(url_for("main.bookmarksPage"))

@main_bp.route("/bookmarks")
def bookmarksPage():
    currentUser, redirectResponse = requireLogin()
    if redirectResponse: return redirectResponse
    userBookmarkList = sorted([item for item in bookmarks if item["userID"] == currentUser["id"]], key=lambda item: item["createdAt"], reverse=True)
    bookmarkedRecipes = []
    for bookmarkData in userBookmarkList:
        recipeData = getRecipeByID(bookmarkData["recipeID"])
        if recipeData:
            recipeCard = buildRecipeCard(recipeData, currentUser["id"])
            recipeCard["createdAt"] = formatDateTime(bookmarkData["createdAt"])
            bookmarkedRecipes.append(recipeCard)
    return render_template("bookmarks.html", bookmarkedRecipes=bookmarkedRecipes)

@main_bp.route("/bookmarks/remove/<recipeID>", methods=["POST"])
def removeBookmark(recipeID: str):
    currentUser, redirectResponse = requireLogin()
    if redirectResponse: return redirectResponse
    targetBookmark = next((item for item in bookmarks if item["userID"] == currentUser["id"] and item["recipeID"] == recipeID), None)
    if targetBookmark is None:
        flash("삭제할 북마크를 찾지 못했습니다.", "error")
        return redirect(url_for("main.bookmarksPage"))
    bookmarks.remove(targetBookmark)
    flash("북마크가 삭제되었습니다.", "success")
    return redirect(url_for("main.bookmarksPage"))

@main_bp.route("/social")
def socialPage():
    currentUser = getCurrentUser()
    availableRecipes = [{"recipeID": r["recipeID"], "recipeName": r["recipeName"]} for r in recipeCatalog]
    socialPostViewList = []
    for postData in sorted(socialPosts, key=lambda item: item["createdAt"], reverse=True):
        writerData = findUserByID(postData["userID"])
        recipeData = getRecipeByID(postData["recipeID"])
        socialPostViewList.append({
            "id": postData["id"], "title": postData["title"], "content": postData["content"], "imagePath": postData["imagePath"],
            "createdAt": formatDateTime(postData["createdAt"]),
            "nickName": writerData["nickName"] if writerData else "알 수 없음",
            "recipeName": recipeData["recipeName"] if recipeData else "레시피 없음",
        })
    return render_template("social.html", availableRecipes=availableRecipes, socialPosts=socialPostViewList, currentUser=currentUser)

@main_bp.route("/social/create", methods=["POST"])
def createSocialPost():
    currentUser, redirectResponse = requireLogin()
    if redirectResponse: return redirectResponse
    recipeID, title, content = request.form.get("recipeID", "").strip(), request.form.get("title", "").strip(), request.form.get("content", "").strip()
    imageFile = request.files.get("imageFile")

    if not recipeID or not title or not content:
        flash("레시피, 제목, 내용을 모두 입력해주세요.", "error")
        return redirect(url_for("main.socialPage"))
    
    imagePath = ""
    if imageFile and imageFile.filename:
        savedName = f"{uuid4().hex}{Path(imageFile.filename).suffix}"
        imageFile.save(Path(current_app.config["UPLOAD_FOLDER"]) / savedName)
        imagePath = f"/static/uploads/{savedName}"

    socialPosts.append({
        "id": getNextID(socialPosts), "userID": currentUser["id"], "recipeID": recipeID,
        "title": title, "content": content, "imagePath": imagePath, "createdAt": getNow()
    })
    flash("후기가 등록되었습니다.", "success")
    return redirect(url_for("main.socialPage"))