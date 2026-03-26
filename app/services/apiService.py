# import re

# def clean_ingredient_name(raw_text):
#     text = re.sub(r'\(.*?\)', '', raw_text)
    
#     text = re.sub(r'[\d\./]+[gml|개|봉지|큰술|작은술|컵|가닥|cm|장|마리|쪽|알]*', '', text)
    
#     text = re.sub(r'[●:,\s]', '', text)
    
#     return text.strip()

# samples = [
#     "오이 70g(1/3개)",
#     "다진 땅콩 10g(1큰술)",
#     "북어채 25g(15개)",
#     "새우 10g(3마리)",
#     "무 30g(5×3×2cm)",
#     "대파 10g(5cm)"
# ]

# for s in samples:
#     print(f"[{s}] -> 결과: {clean_ingredient_name(s)}")

import random
from app.models.recipe import FoodRecipe
from sqlalchemy import func

class ApiService:
    
    @staticmethod
    def getRandomRecommendations(count=4):
        try:
            # 1. DB에서 랜덤하게 count개만큼 쿼리 (ORDER BY RAND())
            random_recipes = FoodRecipe.query.order_by(func.rand()).limit(count).all()
            
            # 2. 템플릿에서 쓰기 편하게 리스트로 가공
            refined_list = []
            for r in random_recipes:
                refined_list.append({
                    "RCP_SEQ": r.RCP_SEQ,          # 모델의 PK 필드명에 맞게 수정
                    "RCP_NM": r.RCP_NM, # 모델 필드명 확인
                    "ATT_FILE_NO_MAIN": r.ATT_FILE_NO_MAIN or "/static/images/default_recipe.jpg",
                    "RCP_PAT2": r.RCP_PAT2,
                    "matchPercent": 0
                })
            return refined_list
            
        except Exception as e:
            print(f"[DB Error] 랜덤 추천 실패: {e}")
            return []