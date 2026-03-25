from flask import Blueprint, request, jsonify
from app.services.fridge_service import FridgeService

fridge_bp = Blueprint('fridge', __name__, url_prefix='/api/fridge')

@fridge_bp.route('/<int:user_id>', methods=['GET'])
def get_fridge_items(user_id):
    """특정 사용자의 냉장고 재료 목록 조회"""
    try:
        items = FridgeService.get_user_ingredients(user_id)
        return jsonify({
            "ok": True,
            "user_id": user_id,
            "count": len(items),
            "items": [item.to_dict() for item in items]
        }), 200
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500

@fridge_bp.route('/add', methods=['POST'])
def add_fridge_item():
    """냉장고에 새로운 재료 추가"""
    data = request.get_json(silent=True) or request.form

    user_id = int(data.get('user_id', 1))  # 테스트용 기본값 1
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
    data = request.get_json(silent=True) or request.form
    user_id = int(data.get('user_id', 1))  # 임시 사용자 ID

    ok, message = FridgeService.delete_ingredient(user_id, ingredient_id)
    
    if ok:
        return jsonify({"ok": True, "message": message, "deleted_id": ingredient_id}), 200
    else:
        # 실패 메시지가 "권한이 없습니다" 등을 포함할 경우 404, DB 에러면 500
        status_code = 500 if "오류" in message else 404
        return jsonify({"ok": False, "message": message}), status_code
