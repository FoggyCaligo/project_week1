from datetime import datetime

from flask import Blueprint, jsonify, request

from app.models.ingredient import UserIngredient
from extensions import db

fridge_bp = Blueprint("fridge", __name__, url_prefix="/api/fridge")


@fridge_bp.route("/<int:userID>", methods=["GET"])
def get_fridge_items(userID):
    """특정 사용자의 냉장고 재료 목록 조회"""
    try:
        items = (
            UserIngredient.query.filter_by(userID=userID)
            .order_by(UserIngredient.expireDate.asc())
            .all()
        )
        return jsonify(
            {
                "ok": True,
                "userID": userID,
                "count": len(items),
                "items": [item.to_dict() for item in items],
            }
        ), 200
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500


@fridge_bp.route("/add", methods=["POST"])
def add_fridge_item():
    """냉장고에 새로운 재료 추가"""
    data = request.get_json(silent=True) or request.form

    userID = data.get("userID", 1)
    ingredientName = (data.get("ingredientName") or "").strip()
    category = (data.get("category") or "").strip()
    expireDateText = (data.get("expireDate") or "").strip()

    if not ingredientName or not category or not expireDateText:
        return jsonify({"ok": False, "message": "ingredientName, category, expireDate는 필수입니다."}), 400

    try:
        expireDate = datetime.strptime(expireDateText, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"ok": False, "message": "expireDate 형식은 YYYY-MM-DD 여야 합니다."}), 400
    # 간단한 정규화 (소문자화 및 띄어쓰기 제거 - 팀원3 매칭용)
    normalizedName = ingredientName.lower().replace(" ", "")

    try:
        newItem = UserIngredient(
            userID=int(userID),
            ingredientName=ingredientName,
            normalizedName=normalizedName,
            category=category,
            expireDate=expireDate,
        )
        db.session.add(newItem)
        db.session.commit()
        return jsonify({"ok": True, "message": "추가 성공", "item": newItem.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "message": f"데이터베이스 저장 오류: {str(e)}"}), 500


@fridge_bp.route("/delete/<int:ingredientID>", methods=["DELETE", "POST"])
def delete_fridge_item(ingredientID):
    """냉장고에서 특정 재료 삭제"""
    # POST를 허용하는 이유는 기본 HTML Form 등에서 쉽게 요청하기 위함
    try:
        item = UserIngredient.query.get(ingredientID)
        if not item:
            return jsonify({"ok": False, "message": "해당 재료를 찾을 수 없습니다."}), 404

        db.session.delete(item)
        db.session.commit()
        return jsonify({"ok": True, "message": "삭제 완료", "deletedID": ingredientID}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "message": f"데이터베이스 삭제 오류: {str(e)}"}), 500
