from flask import Blueprint, render_template, redirect, url_for, flash
from app.services.recipeService import RecipeDetailService
from app.common import getCurrentUser

recipe_bp = Blueprint('recipe', __name__)
recipe_service = RecipeDetailService()

@recipe_bp.route("/recipes/<recipeID>")
def recipeDetailPage(recipeID: str):
    # 1. 로그인한 사용자 정보 가져오기 (재료 일치율 계산용)
    currentUser = getCurrentUser()
    userID = currentUser["id"] if currentUser else None
    
    # 2. 서비스를 통해 레시피 데이터 조회 및 가공
    recipe = recipe_service.get_formatted_recipe(recipeID, user_id=userID)
    
    if recipe is None:
        flash("레시피를 찾지 못했습니다.", "error")
        # 메인 페이지의 추천 목록으로 리다이렉트 (adapter mapping 활용)
        return redirect(url_for("recommendPage"))

    # 3. 상세 페이지 렌더링
    return render_template("recipeDetail.html", recipe=recipe)
