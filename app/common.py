# 기존 app.py에 있던 더미 데이터들과 공통 유틸리티 함수들을 한곳에 모아두는 파일
from datetime import date, datetime
from urllib.parse import quote_plus
from flask import session, flash, redirect, url_for
from werkzeug.security import generate_password_hash

# ==========================================
# 더미 데이터 (앱 시작 시 초기화)
# ==========================================
ingredientAliasMap = {
    "달걀": "계란", "계란": "계란", "파": "대파", "대파": "대파",
    "양파": "양파", "두부": "두부", "우유": "우유", "김치": "김치",
    "돼지고기": "돼지고기", "소고기": "소고기", "밥": "밥", "마늘": "마늘",
    "감자": "감자", "당근": "당근", "애호박": "애호박", "버터": "버터", "간장": "간장",
}


users = []
bookmarks = []
socialPosts = []
recipeCatalog = []

# ==========================================
# 공통 헬퍼 함수들
# ==========================================
def getNow() -> datetime: return datetime.now()
def formatDateTime(value: datetime) -> str: return value.strftime("%Y-%m-%d %H:%M")
def parseDate(dateText: str) -> date | None:
    try: return date.fromisoformat(dateText)
    except ValueError: return None

def normalizeIngredientName(rawName: str) -> str:
    cleanedName = rawName.strip().lower()
    return ingredientAliasMap.get(cleanedName, rawName.strip())

def getNextID(targetList: list[dict]) -> int:
    if not targetList: return 1
    return max(item["id"] for item in targetList) + 1

def findUserByID(userID: int) -> dict | None:
    return next((user for user in users if user["id"] == userID), None)

def findUserByUserName(userName: str) -> dict | None:
    return next((user for user in users if user["userName"] == userName), None)

def getCurrentUser() -> dict | None:
    userID = session.get("userID")
    if not userID: return None
    return findUserByID(userID)

def requireLogin():
    currentUser = getCurrentUser()
    if currentUser is None:
        flash("로그인이 필요합니다.", "error")
        return None, redirect(url_for("auth.loginPage"))
    return currentUser, None

def getRecipeByID(recipeID: str) -> dict | None:
    from app.services.recipeService import RecipeDetailService
    svc = RecipeDetailService()
    return svc.get_formatted_recipe(recipeID)

# DB 연동 (카멜 케이스 및 category 제거)
def getUserIngredientList(userID: int) -> list[dict]:
    from app.models.ingredient import UserIngredient
    items = UserIngredient.query.filter_by(userID=userID).all()
    enrichedList = []
    for item in items:
        daysLeft = (item.expireDate - date.today()).days if item.expireDate else 0
        enrichedList.append({
            "id": item.ID,
            "userID": item.userID,
            "ingredientName": item.ingredientName,
            "normalizedName": item.normalizedName,
            "expireDate": item.expireDate,
            "daysLeft": daysLeft,
            "createdAt": item.createdAt
        })
    enrichedList.sort(key=lambda item: (item["daysLeft"], item["ingredientName"]))
    return enrichedList

def getOwnedIngredientSet(userID: int | None) -> set[str]:
    if userID is None: return set()
    from app.models.ingredient import UserIngredient
    items = UserIngredient.query.filter_by(userID=userID).all()
    ownedSet = set()
    for item in items:
        if item.normalizedName:
            ownedSet.add(item.normalizedName)
    return ownedSet

def getRecipeIngredientNames(recipeData: dict) -> list[str]:
    return [normalizeIngredientName(item["name"]) for item in recipeData["ingredients"]]

def buildShoppingUrl(missingIngredients: list[str]) -> str:
    if not missingIngredients:
        return "https://search.shopping.naver.com/search/all?query=%EB%A0%88%EC%8B%9C%ED%94%BC%20%EC%9E%AC%EB%A3%8C"
    return f"https://search.shopping.naver.com/search/all?query={quote_plus(' '.join(missingIngredients))}"

def buildRecipeCard(recipeData: dict, userID: int | None) -> dict:
    ownedIngredientSet = getOwnedIngredientSet(userID)
    recipeIngredientNames = getRecipeIngredientNames(recipeData)

    haveIngredients = [name for name in recipeIngredientNames if name in ownedIngredientSet]
    missingIngredients = [name for name in recipeIngredientNames if name not in ownedIngredientSet]

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

def buildRecommendedRecipeList(userID: int | None, sortKey: str = "matchPercent", searchKeyword: str = "") -> list[dict]:
    from app.services.recipeService import RecipeDetailService
    from database import db
    from app.models.recipe import Recipe

    loweredKeyword = searchKeyword.strip().lower()
    resultList = []

    svc = RecipeDetailService()
    # 50개의 레시피를 샘플로 가져옵니다 (필요에 따라 limit 조절).
    db_recipes = db.session.query(Recipe).limit(50).all()

    for r in db_recipes:
        recipeData = svc.get_formatted_recipe(r.rcpSeq, userID)
        if not recipeData: continue

        recipeCard = buildRecipeCard(recipeData, userID)
        if loweredKeyword:
            searchableText = " ".join([recipeData["recipeName"], recipeData["description"], " ".join(getRecipeIngredientNames(recipeData))]).lower()
            if loweredKeyword not in searchableText: continue
        resultList.append(recipeCard)

    if sortKey == "missingCount":
        resultList.sort(key=lambda item: (len(item["missingIngredients"]), -item["matchPercent"], item["cookTime"], item["recipeName"]))
    elif sortKey == "cookTime":
        resultList.sort(key=lambda item: (item["cookTime"], -item["matchPercent"], len(item["missingIngredients"]), item["recipeName"]))
    else:
        resultList.sort(key=lambda item: (-item["matchPercent"], len(item["missingIngredients"]), item["cookTime"], item["recipeName"]))
    return resultList

def buildRecipeDetail(recipeID: str, userID: int | None) -> dict | None:
    recipeData = getRecipeByID(recipeID)
    if recipeData is None: return None
    ownedIngredientSet = getOwnedIngredientSet(userID)
    detailIngredients = [{"name": i["name"], "amount": i["amount"], "isOwned": normalizeIngredientName(i["name"]) in ownedIngredientSet} for i in recipeData["ingredients"]]
    recipeIngredientNames = getRecipeIngredientNames(recipeData)
    ownedCount = sum(1 for name in recipeIngredientNames if name in ownedIngredientSet)
    totalCount = len(recipeIngredientNames)
    
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
        "matchPercent": round((ownedCount / totalCount) * 100) if totalCount else 0,
    }

def buildHomeSummary(userID: int) -> dict:
    ingredientList = getUserIngredientList(userID)
    recommendedList = buildRecommendedRecipeList(userID)
    return {
        "ingredientCount": len(ingredientList),
        "expiringCount": len([item for item in ingredientList if item["daysLeft"] <= 3]),
        "recommendCount": len([item for item in recommendedList if item["matchPercent"] > 0]),
    }

def seedDemoData():
    if users: return
    users.append({
        "id": 1, "userName": "demo", "passwordHash": generate_password_hash("demo1234"),
        "nickName": "데모사용자", "createdAt": getNow(),
    })
    bookmarks.append({"id": 1, "userID": 1, "recipeID": "R003", "createdAt": getNow()})
    socialPosts.append({
        "id": 1, "userID": 1, "recipeID": "R003", "title": "간단하게 두부부침",
        "content": "재료가 적게 들어서 빠르게 만들기 좋았습니다.", "imagePath": "", "createdAt": getNow(),
    })

seedDemoData()