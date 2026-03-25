"""
[팀원2(장민재) 작성]
이 파일은 기존 모놀리식 구조의 app.py 파일입니다.
현재 dev 브랜치 방향성에 맞춰, 모든 라우터 로직은 app/routes/ 하위의 블루프린트(Blueprint)로 이관되었습니다.
기존 코드 참고용으로 남겨두며 모든 코드는 주석 처리되었습니다.
실행은 이제 run.py를 통해 진행해주세요.
"""

# # 사전 설치 : pip install flask pymysql requests
# from flask import Flask, render_template, request, jsonify
# from bmi import BMICalculator
# from db import Database
# import atexit   # 애플리케이션 종료시 실행을 요청 (ex. DB연결 종료)
# from datetime import datetime
# 
# app = Flask(__name__)   # Flask 앱 초기화
# db = Database()   # DB 초기화
# 
# # 애플리케이션 종료 시 DB 연결 종료
# atexit.register(db.close)
# 
# @app.route('/', methods=['GET'])
# def index():
#     return render_template('index.html')
# 
# @app.route('/calculate', methods=['POST'])
# def calculate():
#     try:
#         weight = float(request.form['weight'])
#         height = float(request.form['height'])
#         
#         # 입력값 유효성 검사
#         if weight <= 0 or height <= 0:
#             return render_template('index.html', error="체중과 신장은 양수여야 합니다.")
#         
#         # BMI 계산
#         calculator = BMICalculator(weight, height)
#         result = calculator.get_result()
#         
#         # 데이터베이스에 저장
#         db.save_bmi_record(weight, height, result["bmi"], result["category"])
#         
#         return render_template('result.html', 
#                               bmi=result["bmi"], 
#                               category=result["category"],
#                               weight=weight,
#                               height=height)
#     except ValueError:
#         return render_template('index.html', error="유효한 숫자를 입력해주세요.")
# 
# @app.route('/history')
# def history():
#     # 최근 BMI 기록 10개 가져오기
#     records = db.get_bmi_records(10)
#     return render_template('history.html', records=records)
# 
# 
# @app.route('/api/fridge/items', methods=['GET'])
# def getFridgeItems():
#     userId = request.args.get('userId', default=1, type=int)
#     db.ensureUser(userId)
#     items = db.getUserIngredients(userId)
#     return jsonify({
#         "userId": userId,
#         "count": len(items),
#         "items": items
#     })
# 
# 
# @app.route('/api/fridge/add', methods=['POST'])
# def addFridgeItem():
#     payload = request.get_json(silent=True) or request.form
# 
#     userId = int(payload.get('userId', 1))
#     ingredientName = (payload.get('ingredientName') or '').strip()
#     category = (payload.get('category') or '').strip()
#     expireDate = (payload.get('expireDate') or '').strip()
# 
#     if not ingredientName or not category or not expireDate:
#         return jsonify({"ok": False, "message": "필수값 누락"}), 400
# 
#     try:
#         parsedDate = datetime.strptime(expireDate, "%Y-%m-%d").date()
#         if parsedDate.year < 2000 or parsedDate.year > 2100:
#             return jsonify({"ok": False, "message": "유통기한 형식 오류"}), 400
#     except ValueError:
#         return jsonify({"ok": False, "message": "유통기한은 YYYY-MM-DD 형식"}), 400
# 
#     if len(ingredientName) > 120 or len(category) > 50:
#         return jsonify({"ok": False, "message": "문자열 길이 초과"}), 400
# 
#     db.ensureUser(userId)
#     ok, message = db.addUserIngredient(userId, ingredientName, category, expireDate)
#     statusCode = 200 if ok else 500
#     return jsonify({"ok": ok, "message": message}), statusCode
# 
# 
# @app.route('/api/fridge/delete/<int:ingredientId>', methods=['POST', 'DELETE'])
# def deleteFridgeItem(ingredientId):
#     payload = request.get_json(silent=True) or request.form
#     userId = int(payload.get('userId', request.args.get('userId', 1)))
# 
#     deleted = db.deleteUserIngredient(userId, ingredientId)
#     if not deleted:
#         return jsonify({"ok": False, "message": "삭제 대상 없음"}), 404
# 
#     return jsonify({"ok": True, "message": "삭제 완료", "ingredientId": ingredientId})
# 
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
