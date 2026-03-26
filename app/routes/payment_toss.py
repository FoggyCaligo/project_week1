"""
토스페이먼츠 결제창(v2) 연동 — 로그인과 무관하게 결제만 진행.
승인 후 냉장고 적재: 로그인 시 해당 userID, 비로그인 시 FRIDGE_PAYMENT_USER_ID(기본 1).
"""
import base64
import os
import uuid

import requests
from flask import Blueprint, flash, jsonify, redirect, request, session, url_for

from app.services.fridge_service import FridgeService

payment_toss_bp = Blueprint("payment_toss", __name__, url_prefix="/payment/toss")


def _toss_secret_key():
    v = os.getenv("TOSS_SECRET_KEY") or ""
    return v.strip() or None


def _toss_client_key():
    v = os.getenv("TOSS_CLIENT_KEY") or ""
    return v.strip() or None


def _basic_auth_header():
    sk = _toss_secret_key()
    if not sk:
        return None
    token = base64.b64encode(f"{sk}:".encode("utf-8")).decode("utf-8")
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


def _fridge_user_id_for_payment():
    uid = session.get("userID")
    if uid is not None:
        return int(uid)
    return int(os.getenv("FRIDGE_PAYMENT_USER_ID", "1"))


@payment_toss_bp.route("/prepare", methods=["POST"])
def prepare():
    """주문을 세션에 저장하고 결제창에 넘길 값을 반환합니다."""
    client_key = _toss_client_key()
    if not client_key or not _toss_secret_key():
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "토스 키가 없습니다. .env에 TOSS_CLIENT_KEY(API 개별 연동), TOSS_SECRET_KEY를 설정하세요.",
                }
            ),
            503,
        )

    data = request.get_json(silent=True) or {}
    lines = data.get("lines")
    total = data.get("total")

    if not isinstance(lines, list) or len(lines) == 0:
        return jsonify({"ok": False, "message": "주문 항목이 없습니다."}), 400
    if len(lines) > 500:
        return jsonify({"ok": False, "message": "한 번에 담을 수 있는 수량을 초과했습니다."}), 400

    try:
        amount = int(total)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "금액이 올바르지 않습니다."}), 400

    if amount < 100:
        return jsonify({"ok": False, "message": "최소 결제 금액은 100원입니다."}), 400

    clean_lines = []
    for row in lines:
        if not isinstance(row, dict):
            continue
        name = (row.get("ingredient_name") or "").strip()
        exp = (row.get("expire_date") or "").strip()
        cat = (row.get("category") or "").strip() or None
        if not name or not exp:
            continue
        clean_lines.append(
            {"ingredient_name": name[:255], "expire_date": exp[:32], "category": cat}
        )

    if not clean_lines:
        return jsonify({"ok": False, "message": "유효한 주문 행이 없습니다."}), 400

    order_id = f"FRIDGE-{uuid.uuid4().hex[:28]}"

    first = clean_lines[0]["ingredient_name"]
    if len(clean_lines) == 1:
        order_name = first
    else:
        order_name = f"{first} 외 {len(clean_lines) - 1}건"
    if len(order_name) > 100:
        order_name = order_name[:97] + "..."

    session["toss_pending"] = {
        "order_id": order_id,
        "amount": amount,
        "lines": clean_lines,
    }
    session.modified = True

    ck = session.get("toss_customer_key")
    if not ck:
        ck = f"guest_{uuid.uuid4().hex}"
        session["toss_customer_key"] = ck
        session.modified = True

    base = request.host_url.rstrip("/")
    success_url = base + url_for("payment_toss.payment_success")
    fail_url = base + url_for("payment_toss.payment_fail")

    return jsonify(
        {
            "ok": True,
            "clientKey": client_key,
            "orderId": order_id,
            "amount": amount,
            "orderName": order_name,
            "successUrl": success_url,
            "failUrl": fail_url,
            "customerKey": ck,
        }
    )


@payment_toss_bp.route("/success", methods=["GET"])
def payment_success():
    payment_key = request.args.get("paymentKey")
    order_id = request.args.get("orderId")
    amount_raw = request.args.get("amount")

    pending = session.get("toss_pending")
    if not pending or pending.get("order_id") != order_id:
        return redirect(url_for("fridge_views.fridge_index"))

    try:
        amount_i = int(amount_raw)
    except (TypeError, ValueError):
        session.pop("toss_pending", None)
        return redirect(url_for("fridge_views.fridge_index"))

    if amount_i != int(pending.get("amount", -1)):
        session.pop("toss_pending", None)
        return redirect(url_for("fridge_views.fridge_index"))

    headers = _basic_auth_header()
    if not headers:
        session.pop("toss_pending", None)
        return redirect(url_for("fridge_views.fridge_index"))

    try:
        resp = requests.post(
            "https://api.tosspayments.com/v1/payments/confirm",
            headers=headers,
            json={
                "paymentKey": payment_key,
                "orderId": order_id,
                "amount": amount_i,
            },
            timeout=60,
        )
    except requests.RequestException:
        session.pop("toss_pending", None)
        return redirect(url_for("fridge_views.fridge_index"))

    if resp.status_code != 200:
        session.pop("toss_pending", None)
        return redirect(url_for("fridge_views.fridge_index"))

    lines = pending.get("lines") or []
    user_id = _fridge_user_id_for_payment()
    fail = 0
    for row in lines:
        ok, _ = FridgeService.add_ingredient(
            user_id,
            row["ingredient_name"],
            row["expire_date"],
            row.get("category"),
        )
        if not ok:
            fail += 1

    session.pop("toss_pending", None)
    session.modified = True

    if fail == 0:
        flash("토스 결제가 완료되어 냉장고에 담았습니다.", "success")
    elif fail < len(lines):
        flash(f"결제는 완료되었으나 저장에 실패한 품목이 {fail}건 있습니다.", "error")
    else:
        flash("결제는 완료되었으나 냉장고 저장에 실패했습니다.", "error")

    return redirect(url_for("fridge_views.fridge_index"))


@payment_toss_bp.route("/fail", methods=["GET"])
def payment_fail():
    session.pop("toss_pending", None)
    session.modified = True
    flash(request.args.get("message") or "결제가 취소되었거나 실패했습니다.", "error")
    return redirect(url_for("fridge_views.fridge_index"))
