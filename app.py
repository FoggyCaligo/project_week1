from __future__ import annotations

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


app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["UPLOAD_FOLDER"] = str(Path("static") / "uploads")

Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)


ingredientAliasMap = {
    "달걀": "계란",
    "계란": "계란",
    "파": "대파",
    "대파": "대파",
    "양파": "양파",
    "두부": "두부",
    "우유": "우유",
    "김치": "김치",
    "돼지고기": "돼지고기",
    "소고기": "소고기",
    "밥": "밥",
    "마늘": "마늘",
    "감자": "감자",
    "당근": "당근",
    "애호박": "애호박",
    "버터": "버터",
    "간장": "간장",
}


recipeCatalog = [
    {
        "recipeID": "R001",
        "recipeName": "계란볶음밥",
        "description": "남은 밥과 계란으로 빠르게 만들 수 있는 기본 볶음밥입니다.",
        "imageUrl": "https://placehold.co/800x500?text=Egg+Fried+Rice",
        "cookTime": 15,
        "calories": 520,
        "servingSize": 1,
        "nutrition": {
            "carbohydrate": "63g",
            "protein": "18g",
            "fat": "19g",
        },
        "ingredients": [
            {"name": "밥", "amount": "1공기"},
            {"name": "계란", "amount": "2개"},
            {"name": "대파", "amount": "1/2대"},
            {"name": "간장", "amount": "1큰술"},
        ],
        "steps": [
            {
                "title": "재료 준비",
                "description": "대파를 송송 썰고 계란은 풀어둡니다.",
                "imageUrl": "",
            },
            {
                "title": "계란 스크램블",
                "description": "팬에 계란을 먼저 볶아 반쯤 익힌 뒤 덜어둡니다.",
                "imageUrl": "",
            },
            {
                "title": "밥과 함께 볶기",
                "description": "대파를 볶다가 밥, 계란, 간장을 넣고 고르게 볶습니다.",
                "imageUrl": "",
            },
        ],
    },
    {
        "recipeID": "R002",
        "recipeName": "김치찌개",
        "description": "김치와 돼지고기만 있어도 깊은 맛을 낼 수 있는 기본 찌개입니다.",
        "imageUrl": "https://placehold.co/800x500?text=Kimchi+Stew",
        "cookTime": 25,
        "calories": 430,
        "servingSize": 2,
        "nutrition": {
            "carbohydrate": "16g",
            "protein": "28g",
            "fat": "24g",
        },
        "ingredients": [
            {"name": "김치", "amount": "2컵"},
            {"name": "돼지고기", "amount": "150g"},
            {"name": "두부", "amount": "1/2모"},
            {"name": "대파", "amount": "1/2대"},
        ],
        "steps": [
            {
                "title": "재료 볶기",
                "description": "김치와 돼지고기를 먼저 살짝 볶습니다.",
                "imageUrl": "",
            },
            {
                "title": "끓이기",
                "description": "물을 붓고 충분히 끓여 국물 맛을 냅니다.",
                "imageUrl": "",
            },
            {
                "title": "두부 넣기",
                "description": "두부와 대파를 넣고 5분 정도 더 끓입니다.",
                "imageUrl": "",
            },
        ],
    },
    {
        "recipeID": "R003",
        "recipeName": "두부부침",
        "description": "간단하지만 반찬으로 좋은 기본 두부 요리입니다.",
        "imageUrl": "https://placehold.co/800x500?text=Tofu+Steak",
        "cookTime": 10,
        "calories": 260,
        "servingSize": 1,
        "nutrition": {
            "carbohydrate": "8g",
            "protein": "18g",
            "fat": "15g",
        },
        "ingredients": [
            {"name": "두부", "amount": "1모"},
            {"name": "간장", "amount": "1큰술"},
            {"name": "대파", "amount": "약간"},
        ],
        "steps": [
            {
                "title": "두부 물기 제거",
                "description": "키친타월로 두부의 물기를 닦습니다.",
                "imageUrl": "",
            },
            {
                "title": "노릇하게 굽기",
                "description": "팬에 두부를 앞뒤로 노릇하게 굽습니다.",
                "imageUrl": "",
            },
            {
                "title": "양념 곁들이기",
                "description": "간장과 대파를 곁들여 마무리합니다.",
                "imageUrl": "",
            },
        ],
    },
    {
        "recipeID": "R004",
        "recipeName": "감자양파볶음",
        "description": "감자와 양파만으로도 만들 수 있는 쉬운 반찬입니다.",
        "imageUrl": "https://placehold.co/800x500?text=Potato+Stir+Fry",
        "cookTime": 18,
        "calories": 210,
        "servingSize": 2,
        "nutrition": {
            "carbohydrate": "34g",
            "protein": "4g",
            "fat": "6g",
        },
        "ingredients": [
            {"name": "감자", "amount": "2개"},
            {"name": "양파", "amount": "1/2개"},
            {"name": "대파", "amount": "약간"},
        ],
        "steps": [
            {
                "title": "채썰기",
                "description": "감자와 양파를 얇게 채썹니다.",
                "imageUrl": "",
            },
            {
                "title": "감자 익히기",
                "description": "감자를 먼저 볶아 반쯤 익힙니다.",
                "imageUrl": "",
            },
            {
                "title": "양파 넣고 마무리",
                "description": "양파와 대파를 넣고 숨이 죽을 때까지 볶습니다.",
                "imageUrl": "",
            },
        ],
    },
]


users = []
userIngredients = []
bookmarks = []
socialPosts = []


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
    return next((user for user in users if user["id"] == userID), None)


def findUserByUserName(userName: str) -> dict | None:
    return next((user for user in users if user["userName"] == userName), None)


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
    if users:
        return

    demoUser = {
        "id": 1,
        "userName": "demo",
        "passwordHash": generate_password_hash("demo1234"),
        "nickName": "데모사용자",
        "createdAt": getNow(),
    }
    users.append(demoUser)

    userIngredients.extend(
        [
            {
                "id": 1,
                "userID": 1,
                "ingredientName": "달걀",
                "normalizedName": "계란",
                "expireDate": date.today(),
                "createdAt": getNow(),
            },
            {
                "id": 2,
                "userID": 1,
                "ingredientName": "두부",
                "normalizedName": "두부",
                "expireDate": date.today(),
                "createdAt": getNow(),
            },
            {
                "id": 3,
                "userID": 1,
                "ingredientName": "파",
                "normalizedName": "대파",
                "expireDate": date.today(),
                "createdAt": getNow(),
            },
            {
                "id": 4,
                "userID": 1,
                "ingredientName": "김치",
                "normalizedName": "김치",
                "expireDate": date.today(),
                "createdAt": getNow(),
            },
        ]
    )

    bookmarks.append(
        {
            "id": 1,
            "userID": 1,
            "recipeID": "R003",
            "createdAt": getNow(),
        }
    )

    socialPosts.append(
        {
            "id": 1,
            "userID": 1,
            "recipeID": "R003",
            "title": "간단하게 두부부침",
            "content": "재료가 적게 들어서 빠르게 만들기 좋았습니다.",
            "imagePath": "",
            "createdAt": getNow(),
        }
    )


seedDemoData()


@app.route("/")
def home():
    currentUser = getCurrentUser()

    if currentUser:
        summary = buildHomeSummary(currentUser["id"])
        todayRecipes = buildRecommendedRecipeList(currentUser["id"])[:3]
        expiringIngredients = getUserIngredientList(currentUser["id"])[:5]
    else:
        summary = {
            "ingredientCount": 0,
            "expiringCount": 0,
            "recommendCount": 0,
        }
        todayRecipes = buildRecommendedRecipeList(None, sortKey="cookTime")[:3]
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
    userID = currentUser["id"] if currentUser else None

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
        if foundUser is None or not check_password_hash(foundUser["passwordHash"], password):
            flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")
            return redirect(url_for("loginPage"))

        session["userID"] = foundUser["id"]
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

        newUser = {
            "id": getNextID(users),
            "userName": userName,
            "passwordHash": generate_password_hash(password),
            "nickName": nickName,
            "createdAt": getNow(),
        }
        users.append(newUser)

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

    fridgeSummary = buildFridgeSummary(currentUser["id"])
    ingredients = getUserIngredientList(currentUser["id"])

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
        "userID": currentUser["id"],
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
            if item["id"] == id and item["userID"] == currentUser["id"]
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
    currentUser = getCurrentUser()
    sortKey = request.args.get("sort", "matchPercent")
    userID = currentUser["id"] if currentUser else None

    recipes = buildRecommendedRecipeList(userID=userID, sortKey=sortKey)

    return render_template("recommend.html", recipes=recipes)


@app.route("/recipes/<recipeID>")
def recipeDetailPage(recipeID: str):
    currentUser = getCurrentUser()
    userID = currentUser["id"] if currentUser else None

    recipe = buildRecipeDetail(recipeID, userID)
    if recipe is None:
        flash("레시피를 찾지 못했습니다.", "error")
        return redirect(url_for("recommendPage"))

    return render_template("recipe_detail.html", recipe=recipe)


@app.route("/bookmarks/add/<recipeID>", methods=["POST"])
def addBookmark(recipeID: str):
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    recipeData = getRecipeByID(recipeID)
    if recipeData is None:
        flash("북마크할 레시피를 찾지 못했습니다.", "error")
        return redirect(url_for("recommendPage"))

    duplicatedBookmark = next(
        (
            item
            for item in bookmarks
            if item["userID"] == currentUser["id"] and item["recipeID"] == recipeID
        ),
        None,
    )
    if duplicatedBookmark:
        flash("이미 북마크한 레시피입니다.", "info")
        return redirect(url_for("bookmarksPage"))

    bookmarks.append(
        {
            "id": getNextID(bookmarks),
            "userID": currentUser["id"],
            "recipeID": recipeID,
            "createdAt": getNow(),
        }
    )
    flash("북마크에 저장되었습니다.", "success")
    return redirect(url_for("bookmarksPage"))


@app.route("/bookmarks")
def bookmarksPage():
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    userBookmarkList = [item for item in bookmarks if item["userID"] == currentUser["id"]]
    userBookmarkList.sort(key=lambda item: item["createdAt"], reverse=True)

    bookmarkedRecipes = []
    for bookmarkData in userBookmarkList:
        recipeData = getRecipeByID(bookmarkData["recipeID"])
        if recipeData is None:
            continue

        recipeCard = buildRecipeCard(recipeData, currentUser["id"])
        recipeCard["createdAt"] = formatDateTime(bookmarkData["createdAt"])
        bookmarkedRecipes.append(recipeCard)

    return render_template("bookmarks.html", bookmarkedRecipes=bookmarkedRecipes)


@app.route("/bookmarks/remove/<recipeID>", methods=["POST"])
def removeBookmark(recipeID: str):
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    targetBookmark = next(
        (
            item
            for item in bookmarks
            if item["userID"] == currentUser["id"] and item["recipeID"] == recipeID
        ),
        None,
    )

    if targetBookmark is None:
        flash("삭제할 북마크를 찾지 못했습니다.", "error")
        return redirect(url_for("bookmarksPage"))

    bookmarks.remove(targetBookmark)
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
    imageFile = request.files.get("imageFile")

    if not recipeID or not title or not content:
        flash("레시피, 제목, 내용을 모두 입력해주세요.", "error")
        return redirect(url_for("socialPage"))

    recipeData = getRecipeByID(recipeID)
    if recipeData is None:
        flash("선택한 레시피를 찾지 못했습니다.", "error")
        return redirect(url_for("socialPage"))

    imagePath = ""
    if imageFile and imageFile.filename:
        originalName = secure_filename(imageFile.filename)
        suffix = Path(originalName).suffix
        savedName = f"{uuid4().hex}{suffix}"
        savedPath = Path(app.config["UPLOAD_FOLDER"]) / savedName
        imageFile.save(savedPath)
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
    return redirect(url_for("socialPage"))


if __name__ == "__main__":
    app.run(debug=True)