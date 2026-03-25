from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models.ingredient import UserIngredient
from extensions import db

fridge_views_bp = Blueprint("fridge_views", __name__)


@fridge_views_bp.route("/fridge")
def fridge_index():
    """냉장고 페이지 화면 렌더링 (SSR 방식)"""
    userID = 1 # 임시 사용자 ID (나중에 session 연동)
    # DB에서 재료 목록 조회
    items = (
        UserIngredient.query.filter_by(userID=userID)
        .order_by(UserIngredient.expireDate.asc())
        .all()
    )

    ingredients = [item.to_dict() for item in items]

    totalCount = len(ingredients)
    expiringCount = sum(
        1 for item in ingredients if item["daysLeft"] is not None and item["daysLeft"] <= 3
    )
    recommendCount = 3# 임시 (추후 팀원3 API 연동)

    fridgeSummary = {
        "totalCount": totalCount,
        "expiringCount": expiringCount,
        "recommendCount": recommendCount,
    }

    return render_template(
        "fridge.html",
        fridgeSummary=fridgeSummary,
        ingredients=ingredients,
    )


@fridge_views_bp.route("/fridge/add", methods=["POST"])
def add_ingredient():
    """웹 폼(Form)을 통한 식재료 추가"""
    userID = 1
    ingredientName = request.form.get("ingredientName", "").strip()
    expireDateText = request.form.get("expireDate", "").strip()
    category = "기타"# 프론트 임시 폼에 카테고리가 없으므로 기본값

    if not ingredientName or not expireDateText:
        flash("재료명과 유통기한을 모두 입력해주세요.", "error")
        return redirect(url_for("fridge_views.fridge_index"))

    try:
        expireDate = datetime.strptime(expireDateText, "%Y-%m-%d").date()
    except ValueError:
        flash("유통기한 형식이 올바르지 않습니다.", "error")
        return redirect(url_for("fridge_views.fridge_index"))

    normalizedName = ingredientName.lower().replace(" ", "")

    newItem = UserIngredient(
        userID=userID,
        ingredientName=ingredientName,
        normalizedName=normalizedName,
        category=category,
        expireDate=expireDate,
    )
    db.session.add(newItem)
    db.session.commit()

    flash("식재료가 추가되었습니다.", "success")
    return redirect(url_for("fridge_views.fridge_index"))


@fridge_views_bp.route("/fridge/delete/<int:id>", methods=["POST"])
def delete_ingredient(id):
    """웹 폼(Form)을 통한 식재료 삭제"""
    item = UserIngredient.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("식재료가 삭제되었습니다.", "success")
    else:
        flash("해당 식재료를 찾을 수 없습니다.", "error")

    return redirect(url_for("fridge_views.fridge_index"))
