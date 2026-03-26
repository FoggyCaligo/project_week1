# import sys
# from flask import Blueprint, request, jsonify, session
# from app.services.fridge_service import FridgeService

# fridge_bp = Blueprint('fridge', __name__, url_prefix='/api/fridge')

# def get_current_user():
#     try:
#         main_module = sys.modules.get('__main__')
#         if hasattr(main_module, 'getCurrentUser'):
#             return main_module.getCurrentUser()
#     except Exception:
#         pass
#     return None if 'userID' not in session else {'id': session['userID']}

# @fridge_bp.route('/<int:user_id>', methods=['GET'])
# def get_fridge_items(user_id):
#     """특정 사용자의 냉장고 재료 목록 조회"""
#     current_user = get_current_user()
#     if not current_user or user_id != current_user.get('id'):
#         return jsonify({"ok": False, "message": "권한이 없습니다."}), 401
        
#     try:
#         # 정렬 파라미터 가져오기 (기본값: expire_asc)
#         sort_by = request.args.get('sort', 'expire_asc')
        
#         from app.models.ingredient import UserIngredient
#         query = UserIngredient.query.filter_by(user_id=user_id)
        
#         if sort_by == 'expire_asc':
#             query = query.order_by(UserIngredient.expire_date.asc())
#         elif sort_by == 'name_asc':
#             query = query.order_by(UserIngredient.ingredient_name.asc())
#         elif sort_by == 'created_desc':
#             query = query.order_by(UserIngredient.created_at.desc())
#         else:
#             query = query.order_by(UserIngredient.expire_date.asc())
            
#         items = query.all()

#         return jsonify({
#             "ok": True,
#             "user_id": user_id,
#             "count": len(items),
#             "items": [item.to_dict() for item in items]
#         }), 200
#     except Exception as e:
#         return jsonify({"ok": False, "message": str(e)}), 500

# @fridge_bp.route('/recipes', methods=['GET'])
# def get_recommended_recipes():
#     """비동기 방식으로 추천 레시피 가져오기"""
#     current_user = get_current_user()
#     if not current_user:
#         return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
#     user_id = current_user.get('id')
#     try:
#         recipes = FridgeService.get_recommended_recipes(user_id)
#         return jsonify({
#             "ok": True,
#             "recipes": recipes
#         }), 200
#     except Exception as e:
#         return jsonify({"ok": False, "message": str(e)}), 500

# @fridge_bp.route('/item/<int:ingredient_id>', methods=['GET'])
# def get_fridge_item(ingredient_id):
#     """단일 재료 상세 조회"""
#     current_user = get_current_user()
#     if not current_user:
#         return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
#     user_id = current_user.get('id')
#     from app.models.ingredient import UserIngredient
#     item = UserIngredient.query.filter_by(id=ingredient_id, user_id=user_id).first()
    
#     if not item:
#         return jsonify({"ok": False, "message": "재료를 찾을 수 없습니다."}), 404
        
#     return jsonify({"ok": True, "item": item.to_dict()}), 200

# @fridge_bp.route('/edit/<int:ingredient_id>', methods=['PUT', 'POST'])
# def edit_fridge_item(ingredient_id):
#     """냉장고 재료 수정"""
#     current_user = get_current_user()
#     if not current_user:
#         return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
#     data = request.get_json(silent=True) or request.form
#     user_id = current_user.get('id')
#     ingredient_name = (data.get('ingredient_name') or '').strip()
#     category = (data.get('category') or '').strip()
#     expire_date_str = (data.get('expire_date') or '').strip()

#     ok, result = FridgeService.edit_ingredient(user_id, ingredient_id, ingredient_name, category, expire_date_str)
    
#     if ok:
#         return jsonify({"ok": True, "message": "수정 성공", "item": result.to_dict()}), 200
#     else:
#         return jsonify({"ok": False, "message": result}), 400

# @fridge_bp.route('/add', methods=['POST'])
# def add_fridge_item():
#     """냉장고에 새로운 재료 추가"""
#     current_user = get_current_user()
#     if not current_user:
#         return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
#     data = request.get_json(silent=True) or request.form

#     user_id = current_user.get('id')
#     ingredient_name = (data.get('ingredient_name') or '').strip()
#     category = (data.get('category') or '').strip()
#     expire_date_str = (data.get('expire_date') or '').strip()

#     ok, result = FridgeService.add_ingredient(user_id, ingredient_name, category, expire_date_str)
    
#     if ok:
#         return jsonify({"ok": True, "message": "추가 성공", "item": result.to_dict()}), 201
#     else:
#         return jsonify({"ok": False, "message": result}), 400

# @fridge_bp.route('/delete/<int:ingredient_id>', methods=['DELETE', 'POST'])
# def delete_fridge_item(ingredient_id):
#     """냉장고에서 특정 재료 삭제"""
#     current_user = get_current_user()
#     if not current_user:
#         return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
#     user_id = current_user.get('id')

#     ok, message = FridgeService.delete_ingredient(user_id, ingredient_id)
    
#     if ok:
#         return jsonify({"ok": True, "message": message, "deleted_id": ingredient_id}), 200
#     else:
#         status_code = 500 if "오류" in message else 404
#         return jsonify({"ok": False, "message": message}), status_code
import sys
from flask import Blueprint, request, jsonify, session
from app.services.fridge_service import FridgeService
from app.services.authService import AuthService

fridge_bp = Blueprint('fridge', __name__, url_prefix='/api/fridge')

# def get_current_user():
#     try:
#         main_module = sys.modules.get('__main__')
#         if hasattr(main_module, 'getCurrentUser'):
#             return main_module.getCurrentUser()
#     except Exception:
#         pass
#     return None if 'userID' not in session else {'id': session['userID']}

@fridge_bp.route('/infer-category', methods=['GET'])
def infer_ingredient_category():
    """재료명으로 분류 추정(로그인 불필요). 쿼리: q="""
    q = (request.args.get('q') or '').strip()
    if not q:
        return jsonify({"ok": True, "category": "기타"}), 200
    ok, err, norm = FridgeService.validate_ingredient_name(q)
    if not ok:
        return jsonify({"ok": False, "message": err}), 400
    cat = FridgeService.infer_category_from_name(norm)
    return jsonify({"ok": True, "category": cat}), 200


@fridge_bp.route('/resolve-add', methods=['POST'])
def resolve_add_items():
    """
    입력 재료명(콤마 구분)을 받아:
    - 각 토큰을 정규화/검증
    - foodRecipes.RCP_PARTS_DTLS에서 해당 재료가 '존재'하는지 확인
    - 존재하는 것만 category를 추정해서 반환
    """
    data = request.get_json(silent=True) or request.form
    q = (data.get("q") or "").strip()
    tokens, err = FridgeService.parse_ingredient_list_for_query(q)
    if err:
        return jsonify({"ok": False, "message": err}), 400

    found = []
    not_found = []
    for t in tokens:
        matches = FridgeService.search_product_lines_from_recipes(t, max_results=1)
        if matches:
            found.append(
                {
                    "ingredient_name": t,
                    "category": FridgeService.infer_category_from_name(t),
                }
            )
        else:
            not_found.append(t)

    return jsonify({"ok": True, "items": found, "not_found": not_found}), 200


@fridge_bp.route('/add-batch', methods=['POST'])
def add_batch_fridge_items():
    """여러 재료를 amounts와 함께 한 번에 추가합니다."""
    current_user = AuthService.getCurrentUser()
    if not current_user:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401

    data = request.get_json(silent=True) or request.form
    user_id = current_user.ID
    expire_date_str = (data.get("expire_date") or "").strip()
    expire_date_str = expire_date_str if expire_date_str else None

    items = data.get("items") or []
    if not isinstance(items, list) or not items:
        return jsonify({"ok": False, "message": "추가할 재료 목록이 없습니다."}), 400

    added = []
    for it in items:
        ing = (it.get("ingredient_name") or "").strip()
        try:
            amt_raw = it.get("amounts", None)
            if amt_raw is None:
                amt_raw = it.get("amount", None)
            amt = int(amt_raw) if amt_raw is not None else 1
        except (TypeError, ValueError):
            amt = 1

        ok, res = FridgeService.add_ingredient(
            user_id,
            ing,
            expire_date_str=expire_date_str,
            category=None,  # 추가와 동시에 자동 분류
            amounts=amt,
        )
        if not ok:
            return jsonify({"ok": False, "message": res}), 400
        added.append(res.to_dict())

    return jsonify({"ok": True, "added": added}), 201


@fridge_bp.route("/search-products", methods=["GET"])
def search_fridge_products():
    """냉장고 재료 검색: foodRecipes.RCP_PARTS_DTLS에 언급된 실제 표기 수집(로그인 불필요)."""
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"ok": True, "rows": [], "source": "empty"}), 200
    ok, err, norm = FridgeService.validate_ingredient_name(q)
    if not ok:
        return jsonify({"ok": False, "message": err}), 400
    rows = FridgeService.search_product_lines_from_recipes(norm)
    return jsonify({"ok": True, "ingredient_name": norm, "rows": rows, "source": "db"}), 200


@fridge_bp.route('/<int:user_id>', methods=['GET'])
def get_fridge_items(user_id):
    """특정 사용자의 냉장고 재료 목록 조회"""
    current_user = AuthService.getCurrentUser()
    if not current_user or user_id != current_user.ID:
        return jsonify({"ok": False, "message": "권한이 없습니다."}), 401
        
    try:
        sort_by = request.args.get('sort', 'expire_asc')
        from app.models.ingredient import UserIngredient
        
        # 모델 컬럼명에 맞게 수정 (userID)
        query = UserIngredient.query.filter_by(userID=user_id)
        
        if sort_by == 'expire_asc':
            query = query.order_by(UserIngredient.expireDate.asc())
        elif sort_by == 'name_asc':
            query = query.order_by(UserIngredient.ingredientName.asc())
        elif sort_by == 'created_desc':
            query = query.order_by(UserIngredient.createdAt.desc())
        else:
            query = query.order_by(UserIngredient.expireDate.asc())
            
        items = query.all()

        return jsonify({
            "ok": True,
            "user_id": user_id,
            "count": len(items),
            "items": [item.to_dict() for item in items]
        }), 200
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500

@fridge_bp.route('/recipes', methods=['GET'])
def get_recommended_recipes():
    """비동기 방식으로 추천 레시피 가져오기"""
    current_user = AuthService.getCurrentUser()
    if not current_user:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
    user_id = current_user.ID
    try:
        recipes = FridgeService.get_recommended_recipes(user_id)
        return jsonify({
            "ok": True,
            "recipes": recipes
        }), 200
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500

@fridge_bp.route('/item/<int:ingredient_id>', methods=['GET'])
def get_fridge_item(ingredient_id):
    """단일 재료 상세 조회"""
    current_user = AuthService.getCurrentUser()
    if not current_user:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
    user_id = current_user.ID
    from app.models.ingredient import UserIngredient
    
    # ID와 userID로 매칭
    item = UserIngredient.query.filter_by(ID=ingredient_id, userID=user_id).first()
    
    if not item:
        return jsonify({"ok": False, "message": "재료를 찾을 수 없습니다."}), 404
        
    return jsonify({"ok": True, "item": item.to_dict()}), 200

@fridge_bp.route('/edit/<int:ingredient_id>', methods=['PUT', 'POST'])
def edit_fridge_item(ingredient_id):
    """냉장고 재료 수정"""
    current_user = AuthService.getCurrentUser()
    if not current_user:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401

    data = request.get_json(silent=True) or request.form
    user_id = current_user.ID
    ingredient_name = (data.get('ingredient_name') or '').strip()
    expire_date_str = (data.get('expire_date') or '').strip()

    edit_kwargs = {}
    if "category" in data:
        edit_kwargs["category"] = data.get("category")
    ok, result = FridgeService.edit_ingredient(
        user_id, ingredient_id, ingredient_name, expire_date_str, **edit_kwargs
    )
    
    if ok:
        return jsonify({"ok": True, "message": "수정 성공", "item": result.to_dict()}), 200
    else:
        return jsonify({"ok": False, "message": result}), 400

@fridge_bp.route('/add', methods=['POST'])
def add_fridge_item():
    """냉장고에 새로운 재료 추가"""
    current_user = AuthService.getCurrentUser()
    if not current_user:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
    data = request.get_json(silent=True) or request.form

    user_id = current_user.ID
    ingredient_name = (data.get('ingredient_name') or '').strip()
    expire_date_str = (data.get('expire_date') or '').strip()
    expire_date_str = expire_date_str if expire_date_str else None
    category = data.get("category")
    amounts_raw = data.get("amounts", None)
    if amounts_raw is None:
        amounts_raw = data.get("amount", None)
    try:
        amounts_i = int(amounts_raw) if amounts_raw is not None else 1
    except (TypeError, ValueError):
        amounts_i = 1

    ok, result = FridgeService.add_ingredient(
        user_id,
        ingredient_name,
        expire_date_str=expire_date_str,
        category=category,
        amounts=amounts_i,
    )
    
    if ok:
        return jsonify({"ok": True, "message": "추가 성공", "item": result.to_dict()}), 201
    else:
        return jsonify({"ok": False, "message": result}), 400

@fridge_bp.route('/delete/<int:ingredient_id>', methods=['DELETE', 'POST'])
def delete_fridge_item(ingredient_id):
    """냉장고에서 특정 재료 삭제"""
    current_user = AuthService.getCurrentUser()
    if not current_user:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
    user_id = current_user.ID

    ok, message = FridgeService.delete_ingredient(user_id, ingredient_id)
    
    if ok:
        return jsonify({"ok": True, "message": message, "deleted_id": ingredient_id}), 200
    else:
        status_code = 500 if "오류" in message else 404
        return jsonify({"ok": False, "message": message}), status_code