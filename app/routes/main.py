from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.authService import AuthService
from app.services.apiService import ApiService
from app.services.fridge_service import FridgeService
from datetime import datetime, date

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    currentUser = AuthService.getCurrentUser()
    # 기본 랜덤 추천 (비회원용 또는 백업용)
    todayRecipes = ApiService.getRandomRecommendations(4)
    
    summary = {"ingredientCount": 0, "expiringCount": 0, "recommendCount": 0}
    expiringIngredients = []

    if currentUser:
        from app.models.ingredient import UserIngredient
        
        # 1. 내 냉장고 전체 재료 수 (amounts 합산 기준)
        all_items = UserIngredient.query.filter_by(userID=currentUser.ID).all()
        summary["ingredientCount"] = sum(
            (item.amounts if getattr(item, "amounts", None) is not None else 1)
            for item in all_items
        )

        # 2. 유통기한 임박 재료 찾기 (오늘 기준 7일 이내, amounts 합산)
        today = date.today()
        for item in all_items:
            days_left = (item.expireDate - today).days
            if 0 <= days_left <= 7:
                amt = item.amounts if getattr(item, "amounts", None) is not None else 1
                summary["expiringCount"] += amt
                expiringIngredients.append({
                    "ingredientName": item.ingredientName,
                    "daysLeft": days_left,
                    "amounts": amt,
                })

        # 임박순 정렬 (가장 빨리 만료되는 순)
        expiringIngredients.sort(key=lambda x: (x.get("daysLeft", 999999), x.get("ingredientName", "")))
        
        # 🎯 3. [핵심] 랜덤 추천 대신 '내 냉장고 기반 추천' 데이터 가져오기!
        recommended_list = FridgeService.get_recommended_recipes(currentUser.ID)
        
        if recommended_list:
            todayRecipes = recommended_list[:3] # 홈 화면에는 상위 3개만 노출
            summary["recommendCount"] = len(recommended_list)
        else:
            summary["recommendCount"] = 0

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
    sort_type = request.args.get('sort', 'matchPercent') # 정렬값도 받아줍시다!
    
    if raw_query:
        # 검색어가 있으면: 사용자 냉장고 재료 + 입력 재료를 함께 반영해서 계산
        recipes, total_pages = ApiService.searchRecipesFromAPI(
            raw_query,
            user_id=currentUser.ID,
            page=page,
        )
    else:
        # 검색어가 없으면: 기존 냉장고 기반 추천 사용
        recipes = FridgeService.get_recommended_recipes(currentUser.ID)
        total_pages = 1

    # 검색 결과/추천 결과 모두 동일한 기준으로 정렬
    if recipes:
        if sort_type == 'matchPercent':
            recipes.sort(key=lambda x: x.get('matchPercent', 0), reverse=True)
        elif sort_type == 'missingCount':
            recipes.sort(key=lambda x: len(x.get('missingIngredients', [])))
            
            
    return render_template("recommend.html", 
                           recipes=recipes, 
                           total_pages=total_pages,
                           current_page=page,
                           keyword=raw_query,
                           current_sort=sort_type) # 정렬 상태 유지용
@main_bp.route("/recipes")
def allRecipesPage():
    # 1. 입력값 받기
    raw_query = request.args.get("q", "").strip() # 🎯 검색어 추가!
    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort', 'latest')
    
    # 2. [핵심] 검색어가 있으면 검색 서비스로, 없으면 전체 서비스로!
    if raw_query:
        # 검색어와 정렬 조건을 함께 넘겨줍니다. (ApiService에 정렬 로직이 있어야 함)
        recipes, pagination = ApiService.searchRecipesFromDB(raw_query, page=page, sort=sort_type)
    else:
        # 기존의 전체 레시피 로드
        recipes, pagination = ApiService.getAllRecipesWithPagination(page=page, sort=sort_type)
    
    # 3. 렌더링 (keyword를 넘겨줘야 템플릿의 hidden input이 작동합니다)
    return render_template("recipe.html", 
                           recipes=recipes, 
                           pagination=pagination,
                           current_sort=sort_type,
                           keyword=raw_query) # 🎯 템플릿에 검색어 전달!
