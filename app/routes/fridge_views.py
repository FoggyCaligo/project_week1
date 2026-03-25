from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.fridge_service import FridgeService

fridge_views_bp = Blueprint('fridge_views', __name__)

def get_current_user_id():
    # 추후 팀원 인증 로직과 연동 예정 (테스트 편의상 1을 반환하거나 인증 추가)
    return session.get('user_id', 1)

@fridge_views_bp.route('/fridge')
def fridge_index():
    """냉장고 페이지 화면 렌더링 (SSR 방식)"""
    # 로그아웃 상태일 때 500 에러 방지를 위해, user_id 가 없으면 로그인으로 튕겨냄 (현재 주석처리)
    # if 'user_id' not in session:
    #     flash("로그인이 필요합니다.", "warning")
    #     return redirect(url_for('auth.login'))
        
    user_id = get_current_user_id()
    
    # 1. 서비스 계층을 통해 데이터 조회
    items = FridgeService.get_user_ingredients(user_id)
    ingredients = [item.to_dict() for item in items]
    
    totalCount = len(ingredients)
    expiringCount = sum(1 for item in ingredients if item['days_left'] is not None and item['days_left'] <= 3)

    # 2. 추천 레시피 가져오기 (공공 API 연동)
    recommended_recipes = FridgeService.get_recommended_recipes(user_id)
    recommendCount = len(recommended_recipes)

    fridgeSummary = {
        'totalCount': totalCount,
        'expiringCount': expiringCount,
        'recommendCount': recommendCount
    }

    return render_template(
        'fridge.html',
        fridgeSummary=fridgeSummary,
        ingredients=ingredients,
        recommended_recipes=recommended_recipes
    )

@fridge_views_bp.route('/fridge/add', methods=['POST'])
def add_ingredient():
    """웹 폼(Form)을 통한 식재료 추가"""
    user_id = get_current_user_id()
    ingredient_name = request.form.get("ingredient_name", "").strip()
    expire_date_str = request.form.get("expire_date", "").strip()
    category = request.form.get("category", "기타").strip()

    # 서비스 계층 호출
    ok, result = FridgeService.add_ingredient(user_id, ingredient_name, category, expire_date_str)
    
    if ok:
        flash("식재료가 추가되었습니다.", "success")
    else:
        flash(result, "error")

    return redirect(url_for("fridge_views.fridge_index"))

@fridge_views_bp.route('/fridge/delete/<int:id>', methods=['POST'])
def delete_ingredient(id):
    """웹 폼(Form)을 통한 식재료 삭제"""
    user_id = get_current_user_id()
    
    # 서비스 계층 호출
    ok, message = FridgeService.delete_ingredient(user_id, id)
    
    if ok:
        flash("식재료가 삭제되었습니다.", "success")
    else:
        flash(message, "error")
        
    return redirect(url_for("fridge_views.fridge_index"))
