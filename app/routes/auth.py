from flask import Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return "<h1>서버 작동 </h1>"