from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.common import (
     buildHomeSummary, buildRecommendedRecipeList, getUserIngredientList,
     getRecipeByID, getNextID, getNow, bookmarks, socialPosts, buildRecipeCard, formatDateTime, buildRecipeDetail, recipeCatalog
)
from app.services.authService import AuthService
from app.services.apiService import ApiService

main_bp = Blueprint("main", __name__)

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
