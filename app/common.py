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

recipeCatalog = [
    {
        "recipeID": "R001", "recipeName": "계란볶음밥",
        "description": "남은 밥과 계란으로 빠르게 만들 수 있는 기본 볶음밥입니다.",
        "imageUrl": "https://placehold.co/800x500?text=Egg+Fried+Rice",
        "cookTime": 15, "calories": 520, "servingSize": 1,
        "nutrition": {"carbohydrate": "63g", "protein": "18g", "fat": "19g"},
        "ingredients": [
            {"name": "밥", "amount": "1공기"}, {"name": "계란", "amount": "2개"},
            {"name": "대파", "amount": "1/2대"}, {"name": "간장", "amount": "1큰술"},
        ],
        "steps": [
            {"title": "재료 준비", "description": "대파를 송송 썰고 계란은 풀어둡니다.", "imageUrl": ""},
            {"title": "계란 스크램블", "description": "팬에 계란을 먼저 볶아 덜어둡니다.", "imageUrl": ""},
            {"title": "밥과 함께 볶기", "description": "대파를 볶다가 밥, 계란, 간장을 넣고 볶습니다.", "imageUrl": ""},
        ],
    },
    {
        "recipeID": "R002", "recipeName": "김치찌개",
        "description": "김치와 돼지고기만 있어도 깊은 맛을 낼 수 있는 기본 찌개입니다.",
        "imageUrl": "https://placehold.co/800x500?text=Kimchi+Stew",
        "cookTime": 25, "calories": 430, "servingSize": 2,
        "nutrition": {"carbohydrate": "16g", "protein": "28g", "fat": "24g"},
        "ingredients": [
            {"name": "김치", "amount": "2컵"}, {"name": "돼지고기", "amount": "150g"},
            {"name": "두부", "amount": "1/2모"}, {"name": "대파", "amount": "1/2대"},
        ],
        "steps": [
            {"title": "재료 볶기", "description": "김치와 돼지고기를 먼저 살짝 볶습니다.", "imageUrl": ""},
            {"title": "끓이기", "description": "물을 붓고 충분히 끓여 국물 맛을 냅니다.", "imageUrl": ""},
            {"title": "두부 넣기", "description": "두부와 대파를 넣고 5분 정도 더 끓입니다.", "imageUrl": ""},
        ],
    },
    {
        "recipeID": "R003", "recipeName": "두부부침",
        "description": "간단하지만 반찬으로 좋은 기본 두부 요리입니다.",
        "imageUrl": "https://placehold.co/800x500?text=Tofu+Steak",
        "cookTime": 10, "calories": 260, "servingSize": 1,
        "nutrition": {"carbohydrate": "8g", "protein": "18g", "fat": "15g"},
        "ingredients": [
            {"name": "두부", "amount": "1모"}, {"name": "간장", "amount": "1큰술"}, {"name": "대파", "amount": "약간"},
        ],
        "steps": [
            {"title": "두부 물기 제거", "description": "키친타월로 두부의 물기를 닦습니다.", "imageUrl": ""},
            {"title": "노릇하게 굽기", "description": "팬에 두부를 앞뒤로 굽습니다.", "imageUrl": ""},
            {"title": "양념 곁들이기", "description": "간장과 대파를 곁들여 마무리합니다.", "imageUrl": ""},
        ],
    },
    {
        "recipeID": "R004", "recipeName": "감자양파볶음",
        "description": "감자와 양파만으로도 만들 수 있는 쉬운 반찬입니다.",
        "imageUrl": "https://placehold.co/800x500?text=Potato+Stir+Fry",
        "cookTime": 18, "calories": 210, "servingSize": 2,
        "nutrition": {"carbohydrate": "34g", "protein": "4g", "fat": "6g"},
        "ingredients": [
            {"name": "감자", "amount": "2개"}, {"name": "양파", "amount": "1/2개"}, {"name": "대파", "amount": "약간"},
        ],
        "steps": [
            {"title": "채썰기", "description": "감자와 양파를 얇게 채썹니다.", "imageUrl": ""},
            {"title": "감자 익히기", "description": "감자를 먼저 볶아 반쯤 익힙니다.", "imageUrl": ""},
            {"title": "양파 넣고 마무리", "description": "양파와 대파를 넣고 숨이 죽을 때까지 볶습니다.", "imageUrl": ""},
        ],
    },
]

users = []
bookmarks = []
socialPosts = []

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

def requireLogin():
    from app.services.authService import AuthService 
    currentUser = AuthService.getCurrentUser()
    if currentUser is None:
        flash("로그인이 필요합니다.", "error")
        return None, redirect(url_for("auth.loginPage"))
    return currentUser, None

def getRecipeByID(recipeID: str) -> dict | None:
    return next((recipe for recipe in recipeCatalog if recipe["recipeID"] == recipeID), None)

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
    loweredKeyword = searchKeyword.strip().lower()
    resultList = []

    for recipeData in recipeCatalog:
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

# def seedDemoData():
#     if users: return
#     users.append({
#         "id": 1, "userName": "demo", "passwordHash": generate_password_hash("demo1234"),
#         "nickName": "데모사용자", "createdAt": getNow(),
#     })
#     bookmarks.append({"id": 1, "userID": 1, "recipeID": "R003", "createdAt": getNow()})
#     socialPosts.append({
#         "id": 1, "userID": 1, "recipeID": "R003", "title": "간단하게 두부부침",
#         "content": "재료가 적게 들어서 빠르게 만들기 좋았습니다.", "imagePath": "", "createdAt": getNow(),
#     })

# seedDemoData()