# from flask import Blueprint, render_template, request, redirect, url_for, flash, session
# from app.services.fridge_service import FridgeService

# fridge_views_bp = Blueprint('fridge_views', __name__)

# import sys

# def get_current_user():
#     """팀원의 모놀리식 app.py 인메모리 인증 로직과 동기화하여 유효한 사용자인지 검증"""
#     try:
#         main_module = sys.modules.get('__main__')
#         if hasattr(main_module, 'getCurrentUser'):
#             return main_module.getCurrentUser()
#     except Exception:
#         pass
#     return None if 'userID' not in session else {'id': session['userID']}

# @fridge_views_bp.route('/fridge')
# def fridge_index():
#     """냉장고 페이지 화면 렌더링 (SSR 방식)"""
#     current_user = get_current_user()
#     if not current_user:
#         session.pop('userID', None) # 잘못된 세션 초기화
#         flash("로그인이 필요합니다.", "error")
#         return redirect(url_for('loginPage'))
        
#     user_id = current_user['id']
    
#     # 1. 서비스 계층을 통해 데이터 조회
#     items = FridgeService.get_user_ingredients(user_id)
#     ingredients = [item.to_dict() for item in items]
    
#     totalCount = len(ingredients)
#     expiringCount = sum(1 for item in ingredients if item['days_left'] is not None and item['days_left'] <= 3)

#     return render_template(
#         'fridge.html',
#         totalCount=totalCount,
#         expiringCount=expiringCount,
#         ingredients=ingredients
#     )

# @fridge_views_bp.route('/fridge/add', methods=['POST'])
# def add_ingredient():
#     """웹 폼(Form)을 통한 식재료 추가"""
#     user_id = get_current_user_id()
#     ingredient_name = request.form.get("ingredient_name", "").strip()
#     expire_date_str = request.form.get("expire_date", "").strip()
#     category = request.form.get("category", "기타").strip()

#     # 서비스 계층 호출
#     ok, result = FridgeService.add_ingredient(user_id, ingredient_name, category, expire_date_str)
    
#     if ok:
#         flash("식재료가 추가되었습니다.", "success")
#     else:
#         flash(result, "error")

#     return redirect(url_for("fridge_views.fridge_index"))

# @fridge_views_bp.route('/fridge/delete/<int:id>', methods=['POST'])
# def delete_ingredient(id):
#     """웹 폼(Form)을 통한 식재료 삭제"""
#     user_id = get_current_user_id()
    
#     # 서비스 계층 호출
#     ok, message = FridgeService.delete_ingredient(user_id, id)
    
#     if ok:
#         flash("식재료가 삭제되었습니다.", "success")
#     else:
#         flash(message, "error")
        
#     return redirect(url_for("fridge_views.fridge_index"))
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.fridge_service import FridgeService
import sys

fridge_views_bp = Blueprint('fridge_views', __name__)

def get_current_user():
    """팀원의 모놀리식 app.py 인메모리 인증 로직과 동기화하여 유효한 사용자인지 검증"""
    try:
        main_module = sys.modules.get('__main__')
        if hasattr(main_module, 'getCurrentUser'):
            return main_module.getCurrentUser()
    except Exception:
        pass
    return None if 'userID' not in session else {'id': session['userID']}

@fridge_views_bp.route('/fridge')
def fridge_index():
    """냉장고 페이지 화면 렌더링 (SSR 방식)"""
    current_user = get_current_user()
    if not current_user:
        session.pop('userID', None) # 잘못된 세션 초기화
        flash("로그인이 필요합니다.", "error")
        return redirect(url_for('loginPage'))
        
    user_id = current_user['id']
    
    # 1. 서비스 계층을 통해 데이터 조회
    items = FridgeService.get_user_ingredients(user_id)
    ingredients = [item.to_dict() for item in items]
    
    totalCount = len(ingredients)
    expiringCount = sum(1 for item in ingredients if item['days_left'] is not None and item['days_left'] <= 3)

    return render_template(
        'fridge.html',
        totalCount=totalCount,
        expiringCount=expiringCount,
        ingredients=ingredients
    )

@fridge_views_bp.route('/fridge/add', methods=['POST'])
def add_ingredient():
    """웹 폼(Form)을 통한 식재료 추가"""
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('loginPage'))
        
    user_id = current_user['id'] # 버그 수정됨
    ingredient_name = request.form.get("ingredient_name", "").strip()
    expire_date_str = request.form.get("expire_date", "").strip()

    # category 인자 제거
    ok, result = FridgeService.add_ingredient(user_id, ingredient_name, expire_date_str)
    
    if ok:
        flash("식재료가 추가되었습니다.", "success")
    else:
        flash(result, "error")

    return redirect(url_for("fridge_views.fridge_index"))

@fridge_views_bp.route('/fridge/delete/<int:id>', methods=['POST'])
def delete_ingredient(id):
    """웹 폼(Form)을 통한 식재료 삭제"""
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('loginPage'))
        
    user_id = current_user['id'] # 버그 수정됨
    
    # 서비스 계층 호출
    ok, message = FridgeService.delete_ingredient(user_id, id)
    
    if ok:
        flash("식재료가 삭제되었습니다.", "success")
    else:
        flash(message, "error")
        
    return redirect(url_for("fridge_views.fridge_index"))