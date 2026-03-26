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
import requests
from app.models.recipe import Recipe
from sqlalchemy import func

class ApiService:
    
    @staticmethod
    def getRandomRecommendations(count=4):
        try:
            # 1. DB에서 랜덤하게 count개만큼 쿼리 (ORDER BY RAND())
            random_recipes = Recipe.query.order_by(func.rand()).limit(count).all()
            
            # 2. 템플릿에서 쓰기 편하게 리스트로 가공
            refined_list = []
            for r in random_recipes:
                refined_list.append({
                    "recipeID": r.rcpSeq,          # 모델의 PK 필드명에 맞게 수정
                    "RCP_NM": r.rcpNm, # 모델 필드명 확인
                    "ATT_FILE_NO_MAIN": r.attFileNoMain or "/static/images/default_recipe.jpg",
                    "RCP_PAT2": r.rcpPat2,
                    "matchPercent": 0
                })
            return refined_list
            
        except Exception as e:
            print(f"[DB Error] 랜덤 추천 실패: {e}")
            return []
    API_KEY = "sample"
    BASE_URL = f"http://openapi.foodsafetykorea.go.kr/api/{API_KEY}/COOKRCP01/json"

    @staticmethod
    def searchRecipesFromAPI(keyword, page=1):
        """
        [공공데이터 API 전용] 재료명으로 외부 레시피를 검색합니다.
        """
        if not keyword:
            return [], 0

        start = (page - 1) * 10 + 1
        end = start + 10 - 1
        
        # API 요청 URL 조립 (RCP_PARTS_DTLS 파라미터에 검색어 전달)
        # 형식: /시작/종료/RCP_NM=이름&RCP_PARTS_DTLS=재료
        url = f"{ApiService.BASE_URL}/{start}/{end}/RCP_PARTS_DTLS={keyword}"
        print(f"🚀 요청 URL: {url}")  # 1번 단서: URL이 제대로 만들어졌나?
        
        try:
            res = requests.get(url)
            data = res.json()
            
            # 데이터가 없을 경우 처리
            if "COOKRCP01" not in data or data["COOKRCP01"]["total_count"] == "0":
                print(f"[{keyword}] 검색 결과가 없습니다.")
                return [], 0

            total_count = int(data["COOKRCP01"]["total_count"])
            print(f"📊 전체 레시피 개수: {total_count}")
            total_pages = (total_count + 9) // 10 # 10개씩 나눌 때 올림 처리
            
            rows = data["COOKRCP01"].get("row", [])            
            refined_list = []
            
            for r in rows:
                refined_list.append({
                    "recipeID": r.get("RCP_SEQ"),          # 고유 번호
                    "RCP_NM": r.get("RCP_NM"),             # 레시피 이름
                    "ATT_FILE_NO_MAIN": r.get("ATT_FILE_NO_MAIN") or "/static/images/default_recipe.jpg",
                    "RCP_PAT2": r.get("RCP_PAT2", "요리"),  # 카테고리 (국, 반찬 등)
                    "cookTime": 20,                        # API에 없으니 기본값
                    "matchPercent": 100 if keyword in r.get("RCP_PARTS_DTLS", "") else 0
                })
            return refined_list, total_pages

        except Exception as e:
            print(f"[API Search Error]: {e}")
            return [], 1
    @staticmethod
    def getAllRecipesWithPagination(page=1, per_page=10):
        """
        [비회원/전체용] DB에서 전체 레시피를 페이징하여 가져옵니다.
        """
        try:
            # 1. DB에서 최신순(혹은 ID 역순)으로 페이징 쿼리
            pagination = Recipe.query.order_by(Recipe.rcpSeq.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # 2. 템플릿(all_recipes.html) 규격에 맞게 가공
            refined_recipes = []
            for r in pagination.items:
                refined_recipes.append({
                    "recipeID": r.rcpSeq,
                    "recipeName": r.rcpNm,
                    "imageUrl": r.attFileNoMain or "/static/images/default_recipe.jpg",
                    "category": r.rcpPat2 or "일반",
                    "parts_dtls": r.rcpPartsDtls or "", # 전체 레시피 요약용
                })
            
            return refined_recipes, pagination
            
        except Exception as e:
            print(f"[DB Error] 전체 레시피 로드 실패: {e}")
            return [], None
    @staticmethod
    def searchRecipesFromDB(keyword, page=1, per_page=10):
        """
        [비회원/전체용] 우리 DB에서 재료명으로 레시피를 검색합니다.
        """
        try:
            # 1. rcpPartsDtls(재료상세) 컬럼에 키워드가 포함된 것 찾기
            search_term = f"%{keyword}%"
            pagination = Recipe.query.filter(
                Recipe.rcpPartsDtls.like(search_term)
            ).order_by(Recipe.rcpSeq.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

            # 2. 전체 레시피 페이지(all_recipes.html) 규격에 맞게 가공
            refined_recipes = []
            for r in pagination.items:
                refined_recipes.append({
                    "recipeID": r.rcpSeq,
                    "recipeName": r.rcpNm,
                    "imageUrl": r.attFileNoMain or "/static/images/default_recipe.jpg",
                    "category": r.rcpPat2 or "일반",
                    "parts_dtls": r.rcpPartsDtls or "", # 재료 미리보기용
                    "cookTime": 20
                })
            
            return refined_recipes, pagination
        except Exception as e:
            print(f"[DB Search Error]: {e}")
            return [], None