from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.common import (
    getCurrentUser,
    buildHomeSummary,
    buildRecommendedRecipeList,
    getUserIngredientList,
    buildRecipeDetail,
)

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
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

@main_bp.route("/search")
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

@main_bp.route("/recipes/recommend")
def recommendPage():
    currentUser = getCurrentUser()
    sortKey = request.args.get("sort", "matchPercent")
    userID = currentUser["id"] if currentUser else None

    recipes = buildRecommendedRecipeList(userID=userID, sortKey=sortKey)
    return render_template("recommend.html", recipes=recipes)