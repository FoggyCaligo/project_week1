from flask import Blueprint, request, jsonify, session
from app.services.fridge_service import FridgeService

fridge_bp = Blueprint('fridge', __name__, url_prefix='/api/fridge')

@fridge_bp.route('/<int:user_id>', methods=['GET'])
def get_fridge_items(user_id):
    """특정 사용자의 냉장고 재료 목록 조회"""
    if 'userID' not in session and user_id != session.get('userID'):
        return jsonify({"ok": False, "message": "권한이 없습니다."}), 401
        
    try:
        # 정렬 파라미터 가져오기 (기본값: expire_asc)
        sort_by = request.args.get('sort', 'expire_asc')
        
        from app.models.ingredient import UserIngredient
        query = UserIngredient.query.filter_by(user_id=user_id)
        
        if sort_by == 'expire_asc':
            query = query.order_by(UserIngredient.expire_date.asc())
        elif sort_by == 'name_asc':
            query = query.order_by(UserIngredient.ingredient_name.asc())
        elif sort_by == 'created_desc':
            query = query.order_by(UserIngredient.created_at.desc())
        else:
            query = query.order_by(UserIngredient.expire_date.asc())
            
        items = query.all()

        return jsonify({
            "ok": True,
            "user_id": user_id,
            "count": len(items),
            "items": [item.to_dict() for item in items]
        }), 200
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500

@fridge_bp.route('/item/<int:ingredient_id>', methods=['GET'])
def get_fridge_item(ingredient_id):
    """단일 재료 상세 조회"""
    if 'userID' not in session:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
    user_id = session.get('userID')
    from app.models.ingredient import UserIngredient
    item = UserIngredient.query.filter_by(id=ingredient_id, user_id=user_id).first()
    
    if not item:
        return jsonify({"ok": False, "message": "재료를 찾을 수 없습니다."}), 404
        
    return jsonify({"ok": True, "item": item.to_dict()}), 200

@fridge_bp.route('/edit/<int:ingredient_id>', methods=['PUT', 'POST'])
def edit_fridge_item(ingredient_id):
    """냉장고 재료 수정"""
    if 'userID' not in session:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
    data = request.get_json(silent=True) or request.form
    user_id = session.get('userID')
    ingredient_name = (data.get('ingredient_name') or '').strip()
    category = (data.get('category') or '').strip()
    expire_date_str = (data.get('expire_date') or '').strip()

    ok, result = FridgeService.edit_ingredient(user_id, ingredient_id, ingredient_name, category, expire_date_str)
    
    if ok:
        return jsonify({"ok": True, "message": "수정 성공", "item": result.to_dict()}), 200
    else:
        return jsonify({"ok": False, "message": result}), 400

@fridge_bp.route('/add', methods=['POST'])
def add_fridge_item():
    """냉장고에 새로운 재료 추가"""
    if 'userID' not in session:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
    data = request.get_json(silent=True) or request.form

    user_id = session.get('userID')
    ingredient_name = (data.get('ingredient_name') or '').strip()
    category = (data.get('category') or '').strip()
    expire_date_str = (data.get('expire_date') or '').strip()

    ok, result = FridgeService.add_ingredient(user_id, ingredient_name, category, expire_date_str)
    
    if ok:
        return jsonify({"ok": True, "message": "추가 성공", "item": result.to_dict()}), 201
    else:
        return jsonify({"ok": False, "message": result}), 400

@fridge_bp.route('/delete/<int:ingredient_id>', methods=['DELETE', 'POST'])
def delete_fridge_item(ingredient_id):
    """냉장고에서 특정 재료 삭제"""
    if 'userID' not in session:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
        
    user_id = session.get('userID')

    ok, message = FridgeService.delete_ingredient(user_id, ingredient_id)
    
    if ok:
        return jsonify({"ok": True, "message": message, "deleted_id": ingredient_id}), 200
    else:
        status_code = 500 if "오류" in message else 404
        return jsonify({"ok": False, "message": message}), status_code
