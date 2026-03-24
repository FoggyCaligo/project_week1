from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models.ingredient import UserIngredient

fridge_bp = Blueprint('fridge', __name__, url_prefix='/api/fridge')

@fridge_bp.route('/<int:user_id>', methods=['GET'])
def get_fridge_items(user_id):
    """특정 사용자의 냉장고 재료 목록 조회"""
    try:
        # 유통기한 임박 순 정렬
        items = UserIngredient.query.filter_by(user_id=user_id).order_by(UserIngredient.expire_date.asc()).all()
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

    user_id = data.get('user_id', 1)  # 테스트용 기본값 1
    ingredient_name = (data.get('ingredient_name') or '').strip()
    category = (data.get('category') or '').strip()
    expire_date_str = (data.get('expire_date') or '').strip()

    if not ingredient_name or not category or not expire_date_str:
        return jsonify({"ok": False, "message": "필수값(재료명, 카테고리, 유통기한) 누락"}), 400

    try:
        expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"ok": False, "message": "유통기한은 YYYY-MM-DD 형식이어야 합니다."}), 400

    # 간단한 정규화 (소문자화 및 띄어쓰기 제거 - 팀원3 매칭용)
    normalized_name = ingredient_name.lower().replace(" ", "")

    try:
        new_item = UserIngredient(
            user_id=int(user_id),
            ingredient_name=ingredient_name,
            normalized_name=normalized_name,
            category=category,
            expire_date=expire_date
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"ok": True, "message": "추가 성공", "item": new_item.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "message": f"데이터베이스 저장 오류: {str(e)}"}), 500

@fridge_bp.route('/delete/<int:ingredient_id>', methods=['DELETE', 'POST'])
def delete_fridge_item(ingredient_id):
    """냉장고에서 특정 재료 삭제"""
    # POST를 허용하는 이유는 기본 HTML Form 등에서 쉽게 요청하기 위함
    try:
        item = UserIngredient.query.get(ingredient_id)
        if not item:
            return jsonify({"ok": False, "message": "해당 재료를 찾을 수 없습니다."}), 404
            
        db.session.delete(item)
        db.session.commit()
        return jsonify({"ok": True, "message": "삭제 완료", "deleted_id": ingredient_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "message": f"데이터베이스 삭제 오류: {str(e)}"}), 500
