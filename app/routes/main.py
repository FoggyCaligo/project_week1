# 홈페이지('/')와 잡다한 라우트들(검색, 소셜 등)을 담당하는 메인 블루프린트 파일
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from uuid import uuid4
from pathlib import Path
from app.common import (
     buildHomeSummary, buildRecommendedRecipeList, getUserIngredientList,
     getRecipeByID, getNextID, getNow, bookmarks, socialPosts, buildRecipeCard, formatDateTime, buildRecipeDetail, recipeCatalog
)
from app.services.authService import AuthService
from app.services.apiService import ApiService

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    currentUser = AuthService.getCurrentUser()
    todayRecipes = ApiService.getRandomRecommendations(3)
    
    summary = {"ingredientCount": 0, "expiringCount": 0, "recommendCount": 0}
    expiringIngredients = []

    if currentUser:
        pass
    return render_template("home.html", 
                           summary=summary, 
                           todayRecipes=todayRecipes, 
                           expiringIngredients=expiringIngredients,
                           currentUser=currentUser)
# [비회원 전용] 검색 -> 전체 레시피 페이지로 안내
@main_bp.route("/search")
def searchPage():
    raw_query = request.args.get("q", "").strip()
    page = request.args.get('page', 1, type=int) # 페이지 번호도 받아야 함
    
    if not raw_query:
        return redirect(url_for('main.allRecipesPage'))

    recipes, pagination = ApiService.searchRecipesFromDB(raw_query, page=page)

    # is_search 플래그를 넘겨서 검색 결과임을 표시합니다.
    return render_template("recipe.html", 
                           recipes=recipes, 
                           pagination=pagination, # 페이징 객체도 넘겨줘야 함
                           keyword=raw_query,
                           is_search=True)
@main_bp.route("/recipes/recommend")
def recommendPage():
    currentUser, redirectResponse = AuthService.requireLogin()
    if redirectResponse: return redirectResponse

    raw_query = request.args.get("q", "").strip()
    page = request.args.get('page', 1, type=int)
    
    if raw_query:
        # 회원이 검색어를 입력했다면 API에서 가져오기
        recipes, total_pages = ApiService.searchRecipesFromAPI(raw_query, page=page)
    else:
        # 검색어가 없다면 기존처럼 랜덤 추천 (혹은 빈 리스트)
        recipes = ApiService.getRandomRecommendations(12)
        total_pages = 1

    return render_template("recommend.html", 
                           recipes=recipes, 
                           total_pages=total_pages,
                           current_page=page,
                           keyword=raw_query)
@main_bp.route("/recipes")
def allRecipesPage():
    # 1. 입력값만 받아서
    page = request.args.get('page', 1, type=int)
    
    # 2. 서비스에 맡기고 결과만 받음
    recipes, pagination = ApiService.getAllRecipesWithPagination(page=page)
    
    # 3. 서빙(렌더링)
    return render_template("recipe.html", 
                           recipes=recipes, 
                           pagination=pagination)

@main_bp.route("/recipes/<recipeID>")
def recipeDetailPage(recipeID: str):
    currentUser = AuthService.getCurrentUser()
    userID = currentUser["ID"] if currentUser else None
    recipe = buildRecipeDetail(recipeID, userID)
    if recipe is None:
        flash("레시피를 찾지 못했습니다.", "error")
        return redirect(url_for("main.recommendPage"))
    return render_template("recipe_detail.html", recipe=recipe)

@main_bp.route("/bookmarks/add/<recipeID>", methods=["POST"])
def addBookmark(recipeID: str):
    currentUser, redirectResponse = AuthService.requireLogin()
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
    currentUser, redirectResponse = AuthService.requireLogin()
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
    currentUser, redirectResponse = AuthService.requireLogin()
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
    currentUser = AuthService.getCurrentUser()
    availableRecipes = [{"recipeID": r["recipeID"], "recipeName": r["recipeName"]} for r in recipeCatalog]
    socialPostViewList = []
    for postData in sorted(socialPosts, key=lambda item: item["createdAt"], reverse=True):
        writerData = AuthService.findUserByID(postData["userID"])
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
    currentUser, redirectResponse = AuthService.requireLogin()
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