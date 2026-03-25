import re
import os

content = open('app.py', encoding='utf-8').read()

db_setup = """
# ==== [팀원2] DB 설정 및 모델 ====
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:3306/{os.getenv('DB_NAME')}?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class UserIngredient(db.Model):
    __tablename__ = 'user_ingredients'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(100), nullable=False) # 팀원 코드의 UUID와 호환
    ingredient_name = db.Column(db.String(120), nullable=False)
    normalized_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False, default="기타")
    expire_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        days_left = (self.expire_date - datetime.utcnow().date()).days
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ingredientName': self.ingredient_name,
            'normalizedName': self.normalized_name,
            'category': self.category,
            'expireDate': self.expire_date.strftime('%Y-%m-%d'),
            'daysLeft': days_left,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
# ==================================
"""

content = content.replace('app.config["SECRET_KEY"] = "change-this-secret-key"', 'app.config["SECRET_KEY"] = "change-this-secret-key"\n' + db_setup)

new_fridge_logic = """
@app.route("/fridge")
def fridgePage():
    currentUser = getCurrentUser()
    if currentUser is None:
        flash("로그인이 필요합니다.", "warning")
        return redirect(url_for("loginPage"))

    # DB에서 조회
    items = UserIngredient.query.filter_by(user_id=currentUser["id"]).order_by(UserIngredient.expire_date.asc()).all()
    ingredients = [item.to_dict() for item in items]
    
    totalCount = len(ingredients)
    expiringCount = sum(1 for item in ingredients if item['daysLeft'] is not None and item['daysLeft'] <= 3)
    recommendCount = 3 # 임시

    fridgeSummary = {
        'totalCount': totalCount,
        'expiringCount': expiringCount,
        'recommendCount': recommendCount
    }

    return render_template(
        "fridge.html",
        fridgeSummary=fridgeSummary,
        ingredients=ingredients,
    )


@app.route("/fridge/add", methods=["POST"])
def addIngredient():
    currentUser = getCurrentUser()
    if currentUser is None:
        flash("로그인이 필요합니다.", "warning")
        return redirect(url_for("loginPage"))

    ingredientName = request.form.get("ingredientName", "").strip()
    expireDateText = request.form.get("expireDate", "").strip()

    if not ingredientName or not expireDateText:
        flash("재료명과 유통기한을 모두 입력해주세요.", "error")
        return redirect(url_for("fridgePage"))

    try:
        expireDate = datetime.strptime(expireDateText, "%Y-%m-%d").date()
    except ValueError:
        flash("유통기한 형식이 올바르지 않습니다.", "error")
        return redirect(url_for("fridgePage"))

    normalizedName = ingredientName.lower().replace(" ", "")

    new_item = UserIngredient(
        user_id=currentUser["id"],
        ingredient_name=ingredientName,
        normalized_name=normalizedName,
        expire_date=expireDate
    )
    db.session.add(new_item)
    db.session.commit()

    flash("재료가 추가되었습니다.", "success")
    return redirect(url_for("fridgePage"))


@app.route("/fridge/delete/<int:id>", methods=["POST"])
def deleteIngredient(id: int):
    currentUser = getCurrentUser()
    if currentUser is None:
        flash("로그인이 필요합니다.", "warning")
        return redirect(url_for("loginPage"))
        
    item = UserIngredient.query.filter_by(id=id, user_id=currentUser["id"]).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("재료가 삭제되었습니다.", "success")
    else:
        flash("해당 재료를 찾을 수 없습니다.", "error")

    return redirect(url_for("fridgePage"))
"""

# Replace EVERYTHING between @app.route("/fridge") and @app.route("/recipes/recommend")
content = re.sub(r'@app\.route\("/fridge"\).*?(?=@app\.route\("/recipes/recommend"\))', new_fridge_logic + '\n\n', content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied cleanly.")
