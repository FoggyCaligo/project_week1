from __future__ import annotations

from extensions import db
from app.models.user import User
from app.models.bookmark import Bookmark
from app.models.socialPost import SocialPost
from app.models.ingredient import UserIngredient

from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote_plus
from uuid import uuid4

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from db import Database
from repository.recipeDetailRepository import RecipeDetailRepository
from service.recipeDetailService import RecipeDetailService


app = Flask(__name__)

# ==== [팀원2] 블루프린트 및 DB 연동 ====
from extensions import db
app.config.from_object("config.Config")
db.init_app(app)

from app.routes.fridge import fridge_bp
from app.routes.fridge_views import fridge_views_bp
app.register_blueprint(fridge_bp)
app.register_blueprint(fridge_views_bp)
# =======================================

# Initialize DB, Repository and Service
db_instance = Database()
recipe_repo = RecipeDetailRepository(db_instance)
recipe_service = RecipeDetailService(recipe_repo)
app.config["UPLOAD_FOLDER"] = str(Path("static") / "uploads")

Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)


ingredientAliasMap = {
    "달걀": "계란",
    "계란": "계란",
    "파": "대파",
    "대파": "대파",
    "소고기": "소고기",
    "쇠고기": "소고기",
    "밥": "밥",
    "쌀밥":"밥",
    "마가린":"마가린",
    "마아가린":"마가린",
    "간장": "간장",
    "진간장": "간장",
    "양조간장": "간장",
}


recipeCatalog = []

#TODO: 실제 DB 연동으로 변경 필요
users = []
bookmarks = []
socialPosts = []
userIngredients = []


def getNow() -> datetime:
    return datetime.now()


def formatDateTime(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M")


def parseDate(dateText: str) -> date | None:
    try:
        return date.fromisoformat(dateText)
    except ValueError:
        return None


def normalizeIngredientName(rawName: str) -> str:
    cleanedName = rawName.strip().lower()
    return ingredientAliasMap.get(cleanedName, rawName.strip())


def getNextID(targetList: list[dict]) -> int:
    if not targetList:
        return 1
    return max(item["id"] for item in targetList) + 1


def findUserByID(userID: int) -> dict | None:
    return User.query.get(userID)

def findUserByUserName(userName: str) -> dict | None:
    return User.query.filter_by(userName=userName).first()

def getCurrentUser() -> dict | None:
    userID = session.get("userID")
    if not userID:
        return None
    return findUserByID(userID)


@app.context_processor
def injectCommonData():
    return {
        "currentUser": getCurrentUser(),
    }


def requireLogin():
    currentUser = getCurrentUser()
    if currentUser is None:
        flash("로그인이 필요합니다.", "error")
        return None, redirect(url_for("loginPage"))
    return currentUser, None


def getRecipeByID(recipeID: str) -> dict | None:
    return next((recipe for recipe in recipeCatalog if recipe["recipeID"] == recipeID), None)


def getUserIngredientList(userID: int) -> list[dict]:
    filteredList = [item for item in userIngredients if item["userID"] == userID]
    enrichedList = []

    for item in filteredList:
        copiedItem = dict(item)
        copiedItem["daysLeft"] = (copiedItem["expireDate"] - date.today()).days
        enrichedList.append(copiedItem)

    enrichedList.sort(key=lambda item: (item["daysLeft"], item["ingredientName"]))
    return enrichedList


def getOwnedIngredientSet(userID: int | None) -> set[str]:
    if userID is None:
        return set()

    ownedSet = set()
    for item in userIngredients:
        if item["userID"] == userID:
            ownedSet.add(item["normalizedName"])
    return ownedSet


def getRecipeIngredientNames(recipeData: dict) -> list[str]:
    return [normalizeIngredientName(item["name"]) for item in recipeData["ingredients"]]


def buildShoppingUrl(missingIngredients: list[str]) -> str:
    if not missingIngredients:
        return "https://search.shopping.naver.com/search/all?query=%EB%A0%88%EC%8B%9C%ED%94%BC%20%EC%9E%AC%EB%A3%8C"
    searchQuery = quote_plus(" ".join(missingIngredients))
    return f"https://search.shopping.naver.com/search/all?query={searchQuery}"


def buildRecipeCard(recipeData: dict, userID: int | None) -> dict:
    ownedIngredientSet = getOwnedIngredientSet(userID)
    recipeIngredientNames = getRecipeIngredientNames(recipeData)

    haveIngredients = [
        ingredientName
        for ingredientName in recipeIngredientNames
        if ingredientName in ownedIngredientSet
    ]
    missingIngredients = [
        ingredientName
        for ingredientName in recipeIngredientNames
        if ingredientName not in ownedIngredientSet
    ]

    totalCount = len(recipeIngredientNames)
    matchPercent = round((len(haveIngredients) / totalCount) * 100) if totalCount else 0

    return {
        "recipeID": recipeData["recipeID"],
        "recipeName": recipeData["recipeName"],
        "description": recipeData["description"],
        "imageUrl": recipeData["imageUrl"],
        "cookTime": recipeData["cookTime"],
        "matchPercent": matchPercent,
        "haveIngredients": haveIngredients,
        "missingIngredients": missingIngredients,
        "shoppingUrl": buildShoppingUrl(missingIngredients),
    }


def buildRecommendedRecipeList(
    userID: int | None,
    sortKey: str = "matchPercent",
    searchKeyword: str = "",
) -> list[dict]:
    loweredKeyword = searchKeyword.strip().lower()
    resultList = []

    for recipeData in recipeCatalog:
        recipeCard = buildRecipeCard(recipeData, userID)

        if loweredKeyword:
            searchableText = " ".join(
                [
                    recipeData["recipeName"],
                    recipeData["description"],
                    " ".join(getRecipeIngredientNames(recipeData)),
                ]
            ).lower()

            if loweredKeyword not in searchableText:
                continue

        resultList.append(recipeCard)

    if sortKey == "missingCount":
        resultList.sort(
            key=lambda item: (
                len(item["missingIngredients"]),
                -item["matchPercent"],
                item["cookTime"],
                item["recipeName"],
            )
        )
    elif sortKey == "cookTime":
        resultList.sort(
            key=lambda item: (
                item["cookTime"],
                -item["matchPercent"],
                len(item["missingIngredients"]),
                item["recipeName"],
            )
        )
    else:
        resultList.sort(
            key=lambda item: (
                -item["matchPercent"],
                len(item["missingIngredients"]),
                item["cookTime"],
                item["recipeName"],
            )
        )

    return resultList


def buildRecipeDetail(recipeID: str, userID: int | None) -> dict | None:
    recipeData = getRecipeByID(recipeID)
    if recipeData is None:
        return None

    ownedIngredientSet = getOwnedIngredientSet(userID)
    detailIngredients = []

    for ingredientData in recipeData["ingredients"]:
        normalizedName = normalizeIngredientName(ingredientData["name"])
        detailIngredients.append(
            {
                "name": ingredientData["name"],
                "amount": ingredientData["amount"],
                "isOwned": normalizedName in ownedIngredientSet,
            }
        )

    recipeIngredientNames = getRecipeIngredientNames(recipeData)
    ownedCount = sum(
        1 for ingredientName in recipeIngredientNames if ingredientName in ownedIngredientSet
    )
    totalCount = len(recipeIngredientNames)
    matchPercent = round((ownedCount / totalCount) * 100) if totalCount else 0

    return {
        "recipeID": recipeData["recipeID"],
        "recipeName": recipeData["recipeName"],
        "description": recipeData["description"],
        "imageUrl": recipeData["imageUrl"],
        "cookTime": recipeData["cookTime"],
        "calories": recipeData["calories"],
        "servingSize": recipeData["servingSize"],
        "nutrition": recipeData["nutrition"],
        "ingredients": detailIngredients,
        "steps": recipeData["steps"],
        "matchPercent": matchPercent,
    }


def buildHomeSummary(userID: int) -> dict:
    ingredientList = getUserIngredientList(userID)
    recommendedList = buildRecommendedRecipeList(userID)

    return {
        "ingredientCount": len(ingredientList),
        "expiringCount": len([item for item in ingredientList if item["daysLeft"] <= 3]),
        "recommendCount": len([item for item in recommendedList if item["matchPercent"] > 0]),
    }


def buildFridgeSummary(userID: int) -> dict:
    ingredientList = getUserIngredientList(userID)
    recommendedList = buildRecommendedRecipeList(userID)

    return {
        "totalCount": len(ingredientList),
        "expiringCount": len([item for item in ingredientList if item["daysLeft"] <= 3]),
        "recommendCount": len([item for item in recommendedList if item["matchPercent"] > 0]),
    }

def seedDemoData():
    if User.query.filter_by(userName="demo").first():
        return

    demoUser = User(
        userName="demo",
        passwordHash=generate_password_hash("demo1234"),
        nickName="데모사용자",
    )
    db.session.add(demoUser)
    db.session.commit()


with app.app_context():
    seedDemoData()


@app.route("/")
def home():
    currentUser = getCurrentUser()

    if currentUser:
        summary = buildHomeSummary(currentUser.id)
        todayRecipes = recipe_service.get_recipe_list(limit=10)
        expiringIngredients = getUserIngredientList(currentUser.id)[:5]
    else:
        summary = {
            "ingredientCount": 0,
            "expiringCount": 0,
            "recommendCount": 0,
        }
        todayRecipes = recipe_service.get_recipe_list(limit=10)
        expiringIngredients = []

    return render_template(
        "home.html",
        summary=summary,
        todayRecipes=todayRecipes,
        expiringIngredients=expiringIngredients,
    )


@app.route("/search")
def searchPage():
    currentUser = getCurrentUser()
    searchKeyword = request.args.get("q", "").strip()
    userID = currentUser.id if currentUser else None

    recipes = buildRecommendedRecipeList(
        userID=userID,
        sortKey="matchPercent",
        searchKeyword=searchKeyword,
    )

    return render_template("recommend.html", recipes=recipes)

@app.route("/login", methods=["GET", "POST"])
def loginPage():
    if request.method == "POST":
        userName = request.form.get("userName", "").strip()
        password = request.form.get("password", "").strip()

        foundUser = findUserByUserName(userName)
        if foundUser is None or not check_password_hash(foundUser.passwordHash, password):
            flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")
            return redirect(url_for("loginPage"))

        session["userID"] = foundUser.id
        flash("로그인되었습니다.", "success")
        return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signupPage():
    if request.method == "POST":
        userName = request.form.get("userName", "").strip()
        nickName = request.form.get("nickName", "").strip()
        password = request.form.get("password", "").strip()
        passwordConfirm = request.form.get("passwordConfirm", "").strip()

        if not userName or not nickName or not password:
            flash("모든 항목을 입력해주세요.", "error")
            return redirect(url_for("signupPage"))

        if password != passwordConfirm:
            flash("비밀번호 확인이 일치하지 않습니다.", "error")
            return redirect(url_for("signupPage"))

        if findUserByUserName(userName):
            flash("이미 사용 중인 아이디입니다.", "error")
            return redirect(url_for("signupPage"))

        newUser = User(
            userName=userName,
            passwordHash=generate_password_hash(password),
            nickName=nickName,
        )
        db.session.add(newUser)
        db.session.commit()

        flash("회원가입이 완료되었습니다. 로그인해주세요.", "success")
        return redirect(url_for("loginPage"))

    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("로그아웃되었습니다.", "success")
    return redirect(url_for("home"))


@app.route("/fridge")
def fridgePage():
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    fridgeSummary = buildFridgeSummary(currentUser.id)
    ingredients = getUserIngredientList(currentUser.id)

    return render_template(
        "fridge.html",
        fridgeSummary=fridgeSummary,
        ingredients=ingredients,
    )


@app.route("/fridge/add", methods=["POST"])
def addIngredient():
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    ingredientName = request.form.get("ingredientName", "").strip()
    expireDateText = request.form.get("expireDate", "").strip()

    if not ingredientName or not expireDateText:
        flash("재료명과 유통기한을 모두 입력해주세요.", "error")
        return redirect(url_for("fridgePage"))

    expireDate = parseDate(expireDateText)
    if expireDate is None:
        flash("유통기한 형식이 올바르지 않습니다.", "error")
        return redirect(url_for("fridgePage"))

    newIngredient = {
        "id": getNextID(userIngredients),
        "userID": currentUser.id,
        "ingredientName": ingredientName,
        "normalizedName": normalizeIngredientName(ingredientName),
        "expireDate": expireDate,
        "createdAt": getNow(),
    }
    userIngredients.append(newIngredient)

    flash("재료가 추가되었습니다.", "success")
    return redirect(url_for("fridgePage"))


@app.route("/fridge/delete/<int:id>", methods=["POST"])
def deleteIngredient(id: int):
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    targetIngredient = next(
        (
            item
            for item in userIngredients
            if item["id"] == id and item["userID"] == currentUser.id
        ),
        None,
    )

    if targetIngredient is None:
        flash("삭제할 재료를 찾지 못했습니다.", "error")
        return redirect(url_for("fridgePage"))

    userIngredients.remove(targetIngredient)
    flash("재료가 삭제되었습니다.", "success")
    return redirect(url_for("fridgePage"))


@app.route("/recipes/recommend")
def recommendPage():
    # Fetch from the real database service
    recipes = recipe_service.get_recipe_list(limit=20)

    return render_template("recommend.html", recipes=recipes)


@app.route("/recipes/<recipeID>")
def recipeDetailPage(recipeID: str):
    # Fetch data using the new service and repository
    recipe = recipe_service.get_formatted_recipe(recipeID)
    
    if recipe is None:
        flash("레시피를 찾지 못했습니다.", "error")
        return redirect(url_for("recommendPage"))

    return render_template("recipe_detail.html", recipe=recipe)

@app.route("/bookmarks/add/<recipeID>", methods=["POST"])
def addBookmark(recipeID: str):
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    duplicatedBookmark = Bookmark.query.filter_by(
        userID=currentUser.id,
        recipeID=recipeID
    ).first()

    if duplicatedBookmark:
        flash("이미 북마크한 레시피입니다.", "info")
        return redirect(url_for("bookmarksPage"))

    bookmark = Bookmark(
        userID=currentUser.id,
        recipeID=recipeID,
    )
    db.session.add(bookmark)
    db.session.commit()

    flash("북마크에 저장되었습니다.", "success")
    return redirect(url_for("bookmarksPage"))

@app.route("/bookmarks")
def bookmarksPage():
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    userBookmarkList = [item for item in bookmarks if item["userID"] == currentUser.id]
    userBookmarkList.sort(key=lambda item: item["createdAt"], reverse=True)

    bookmarkedRecipes = []
    for bookmarkData in userBookmarkList:
        recipeData = getRecipeByID(bookmarkData["recipeID"])
        if recipeData is None:
            continue

        recipeCard = buildRecipeCard(recipeData, currentUser.id)
        recipeCard["createdAt"] = formatDateTime(bookmarkData["createdAt"])
        bookmarkedRecipes.append(recipeCard)

    return render_template("bookmarks.html", bookmarkedRecipes=bookmarkedRecipes)

@app.route("/bookmarks/remove/<recipeID>", methods=["POST"])
def removeBookmark(recipeID: str):
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    targetBookmark = Bookmark.query.filter_by(
        userID=currentUser.id,
        recipeID=recipeID
    ).first()

    if targetBookmark is None:
        flash("삭제할 북마크를 찾지 못했습니다.", "error")
        return redirect(url_for("bookmarksPage"))

    db.session.delete(targetBookmark)
    db.session.commit()

    flash("북마크가 삭제되었습니다.", "success")
    return redirect(url_for("bookmarksPage"))

@app.route("/social")
def socialPage():
    currentUser = getCurrentUser()

    availableRecipes = [
        {
            "recipeID": recipeData["recipeID"],
            "recipeName": recipeData["recipeName"],
        }
        for recipeData in recipeCatalog
    ]

    socialPostViewList = []
    sortedPostList = sorted(socialPosts, key=lambda item: item["createdAt"], reverse=True)

    for postData in sortedPostList:
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

@app.route("/social/create", methods=["POST"])
def createSocialPost():
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    recipeID = request.form.get("recipeID", "").strip()
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    imagePath = ""

    if not recipeID or not title or not content:
        flash("모든 항목을 입력해주세요.", "error")
        return redirect(url_for("socialPage"))

    post = SocialPost(
        userID=currentUser.id,
        recipeID=recipeID,
        title=title,
        content=content,
        imagePath=imagePath,
    )
    db.session.add(post)
    db.session.commit()

    flash("게시글이 등록되었습니다.", "success")
    return redirect(url_for("socialPage"))

if __name__ == "__main__":
    app.run(debug=True)
