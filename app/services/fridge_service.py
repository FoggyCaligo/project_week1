# import os
# from datetime import datetime
# from app.models.ingredient import UserIngredient
# # extensions 대신 새로 만든 통합 database 파일에서 db를 가져옵니다.
# from database import db

# class FridgeService:
#     @staticmethod
#     def get_user_ingredients(user_id):
#         """특정 사용자의 냉장고 재료 목록을 유통기한 임박 순으로 조회합니다."""
#         return UserIngredient.query.filter_by(user_id=user_id).order_by(UserIngredient.expire_date.asc()).all()

#     @staticmethod
#     def add_ingredient(user_id, ingredient_name, category, expire_date_str):
#         """냉장고에 새로운 재료를 추가합니다."""
#         if not ingredient_name or not expire_date_str:
#             return False, "재료명과 유통기한을 모두 입력해주세요."
            
#         try:
#             expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
#         except ValueError:
#             return False, "유통기한은 YYYY-MM-DD 형식이어야 합니다."

#         normalized_name = ingredient_name.lower().replace(" ", "")
#         if not category:
#             category = "기타"
            
#         # 팀원의 인메모리 인증으로 인해 DB users 테이블에 사용자가 없을 경우 외래키 에러 방지용 임시 생성 (db.py의 ensureUser 로직)
#         from sqlalchemy import text
#         try:
#             db.session.execute(
#                 text("INSERT IGNORE INTO users (ID, userName, passwordHash, nickName) VALUES (:id, :un, :pw, :nn)"),
#                 {"id": user_id, "un": f"user_{user_id}", "pw": "dummy_hash", "nn": f"User {user_id}"}
#             )
#             db.session.commit()
#         except Exception:
#             db.session.rollback()
        
#         new_item = UserIngredient(
#             user_id=user_id,
#             ingredient_name=ingredient_name,
#             normalized_name=normalized_name,
#             category=category,
#             expire_date=expire_date
#         )
        
#         try:
#             db.session.add(new_item)
#             db.session.commit()
#             return True, new_item
#         except Exception as e:
#             db.session.rollback()
#             return False, f"데이터베이스 저장 오류: {str(e)}"

#     @staticmethod
#     def edit_ingredient(user_id, ingredient_id, ingredient_name, category, expire_date_str):
#         """냉장고 재료 정보를 수정합니다."""
#         item = UserIngredient.query.filter_by(id=ingredient_id, user_id=user_id).first()
#         if not item:
#             return False, "해당 재료를 찾을 수 없습니다."
            
#         if not ingredient_name or not expire_date_str:
#             return False, "재료명과 유통기한을 모두 입력해주세요."
            
#         try:
#             expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
#         except ValueError:
#             return False, "유통기한은 YYYY-MM-DD 형식이어야 합니다."

#         item.ingredient_name = ingredient_name
#         item.normalized_name = ingredient_name.lower().replace(" ", "")
#         item.category = category if category else "기타"
#         item.expire_date = expire_date
        
#         try:
#             db.session.commit()
#             return True, item
#         except Exception as e:
#             db.session.rollback()
#             return False, f"데이터베이스 저장 오류: {str(e)}"

#     @staticmethod
#     def delete_ingredient(user_id, ingredient_id):
#         """냉장고에서 특정 재료를 삭제합니다."""
#         item = UserIngredient.query.filter_by(id=ingredient_id, user_id=user_id).first()
#         if not item:
#             return False, "해당 재료를 찾을 수 없거나 삭제 권한이 없습니다."
            
#         try:
#             db.session.delete(item)
#             db.session.commit()
#             return True, "삭제 완료"
#         except Exception as e:
#             db.session.rollback()
#             return False, f"데이터베이스 삭제 오류: {str(e)}"

#     @staticmethod
#     def get_recommended_recipes(user_id):
#         """
#         사용자의 냉장고 재료 중 유통기한이 임박한 재료를 기반으로
#         공공데이터 API(COOKRCP01)를 활용하여 추천 레시피를 가져옵니다.
#         """
#         # 1. 유통기한이 가장 임박한 재료 최대 2개 추출
#         items = UserIngredient.query.filter_by(user_id=user_id).order_by(UserIngredient.expire_date.asc()).limit(2).all()
        
#         if not items:
#             return []
            
#         # 재료명 추출 (예: '새우', '가지')
#         ingredient_names = [item.ingredient_name for item in items]
#         search_query = ",".join(ingredient_names)
        
#         # 2. 공공 API 호출
#         api_key = "3601fcadc33549809411"  # 발급받은 OpenAPI 인증키
#         url = f"https://openapi.foodsafetykorea.go.kr/api/{api_key}/COOKRCP01/json/1/3/RCP_PARTS_DTLS=\"{search_query}\""
        
#         import requests
#         try:
#             response = requests.get(url, timeout=5)
#             data = response.json()
            
#             if "COOKRCP01" in data and "row" in data["COOKRCP01"]:
#                 recipes = data["COOKRCP01"]["row"]
                
#                 # 프론트엔드에 전달하기 좋게 가공
#                 # 스네이크 있다고 뭐라하는거 나올 수 있는데 openapi 파라미터가 스네이크여서 그거 따라갔음.
#                 # 필요할 때 바꿈.
#                 recommended = []
#                 for r in recipes:
#                     recommended.append({
#                         "recipeID": r.get("RCP_SEQ"),
#                         "recipeName": r.get("RCP_NM"),
#                         "imageUrl": r.get("ATT_FILE_NO_MAIN"),
#                         "description": r.get("RCP_WAY2") + " | " + r.get("RCP_PAT2"),
#                     })
#                 return recommended
#             return []
#         except Exception as e:
#             print(f"API 호출 오류: {e}")
#             return []

import os
import re
import requests
from datetime import datetime, date, timedelta
from app.models.ingredient import UserIngredient
from database import db
from sqlalchemy import text, func

ALLOWED_INGREDIENT_CATEGORIES = frozenset({
    "채소", "과일", "육류", "수산물", "유제품", "가공식품", "기타",
})

_CATEGORY_OMITTED = object()

# 재료명: 한글만 허용 (검색 input 제약)
_INGREDIENT_NAME_PATTERN = re.compile(r"^[\uAC00-\uD7A3]+$")

# (분류, 키워드) — 카테고리 순서 중요: 가공식품을 채소보다 먼저 두어 '파스타'가 단독 '파'(채소)에 걸리지 않게 함.
# 채소는 과일보다 앞에 두어 '배추'가 과일 '배'에 걸리지 않게 함.
_CATEGORY_KEYWORD_RULES = (
    ("수산물", ["전복", "고등어", "연어", "참치", "생선", "오징어", "문어", "낙지", "홍합", "멸치", "다시마", "미역", "새우", "조개", "굴", "김"]),
    ("육류", ["소고기", "돼지고기", "닭고기", "삼겹", "목살", "안심", "소시지", "베이컨", "곱창", "양고기", "햄", "닭", "돼지"]),
    ("유제품", ["요거트", "요구르트", "치즈", "버터", "우유", "크림"]),
    ("가공식품", ["파스타", "스파게티", "고추장", "된장", "통조림", "식용유", "라면", "과자", "빵", "간장", "설탕", "소금", "김치", "두부"]),
    ("채소", [
        "브로콜리", "콩나물", "애호박", "청경채", "깻잎", "시금치", "상추", "배추", "토마토", "피망",
        "쪽파", "대파", "신파", "실파", "부추", "미나리", "열무", "당근", "양파", "마늘",
        "감자", "고구마", "가지", "오이", "버섯", "무우", "숙주", "파",
    ]),
    ("과일", ["바나나", "복숭아", "오렌지", "딸기", "수박", "참외", "망고", "키위", "포도", "사과", "배", "귤"]),
)

# 식재료 키워드에 없는 일반 명사·가구·전자기기 등(부분 일치 시 거부)
_NONFOOD_NAME_FRAGMENTS = frozenset({
    "쇼파", "소파", "침대", "책상", "의자", "책장", "옷장", "화장실", "거실",
    "컴퓨터", "노트북", "스마트폰", "핸드폰", "태블릿", "에어컨", "세탁기", "냉장고",
    "텔레비전", "티비",
    "자동차", "자전거", "오토바이", "비행기", "기차", "지하철", "버스", "택시",
    "아파트", "건물", "학교", "회사",
})

# normalizedName 표준화 규칙
_NORMALIZE_KEYWORD_RULES = (
    ("게", ["꽃게", "대게", "홍게", "털게", "참게", "방게", "게"]),
    ("오징어", ["갑오징어", "무늬오징어", "대왕오징어", "살오징어", "꼴뚜기", "오징어"]),
    ("김", ["돌김", "파래김", "재래김", "곱창김", "조미김", "김"]),
    ("미역", ["실미역", "줄기미역", "산모미역", "미역"]),
    ("멸치", ["잔멸치", "지리멸치", "중멸치", "대멸치", "멸치"]),
    ("버섯", ["팽이버섯", "양송이버섯", "표고버섯", "새송이버섯", "느타리버섯", "목이버섯", "송이버섯", "버섯"]),
    ("고추", ["청양고추", "꽈리고추", "오이고추", "풋고추", "홍고추", "칠리고추", "고추"]),
    ("콩", ["검은콩", "강낭콩", "완두콩", "병아리콩", "렌틸콩", "메주콩", "땅콩", "콩"]),
    ("파", ["대파", "쪽파", "실파", "파"]),
    ("호박", ["애호박", "단호박", "늙은호박", "둥근호박", "돼지호박", "쥬키니", "주키니", "호박"]),
    ("무", ["총각무", "알타리무", "열무", "쌈무", "단무지", "무"]),
    ("마늘", ["통마늘", "깐마늘", "다진마늘", "흑마늘", "마늘"]),
    ("감자", ["수미감자", "두백감자", "돼지감자", "홍감자", "햇감자", "감자"]),
    ("고기", ["소고기", "돼지고기", "닭고기", "양고기", "오리고기", "뒷고기", "고기"]),
    ("면", ["소면", "중면", "당면", "우동면", "쫄면", "라면", "파스타면", "옥수수면", "면"]),
    ("가루", ["밀가루", "쌀가루", "부침가루", "튀김가루", "빵가루", "콩가루", "고춧가루"]),
    ("치즈", ["모짜렐라치즈", "체다치즈", "크림치즈", "파마산치즈", "리코타치즈", "치즈"]),
    ("소금", ["맛소금", "구운소금", "꽃소금", "굵은소금", "허브소금", "소금"]),
    ("장", ["된장", "고추장", "쌈장", "춘장", "막장", "간장", "장"]),
    ("조개", ["바지락", "모시조개", "백합", "키조개", "가리비", "전복", "홍합", "굴", "조개"]),
    ("젓갈", ["새우젓", "멸치젓", "갈치속젓", "명란젓", "창란젓", "오징어젓"]),
    ("떡", ["가래떡", "떡국떡", "인절미", "백설기", "찹쌀떡", "떡"]),
    ("계란", ["달걀", "메추리알", "유정란", "반숙란", "삶은계란", "계란"]),
    ("식초", ["양조식초", "사과식초", "발사믹식초", "현미식초", "식초"]),
    ("올리브유", ["올리브오일", "올리브유"]),
    ("식용유", ["식용유", "오일"]),
    ("설탕", ["백설탕", "흑설탕", "황설탕", "슈가파우더", "시럽", "설탕"]),
    ("시럽", ["메이플시럽", "아가베시럽", "초코시럽", "카라멜시럽", "시럽"]),
    ("카레", ["고형카레", "카레가루", "인도카레", "버터치킨카레", "카레"]),
    ("육수", ["멸치육수", "사골육수", "닭육수", "채소육수", "코인육수", "육수"]),
    ("국물", ["된장국", "미역국", "김치국", "맑은국"]),
    ("김치", ["배추김치", "깍두기", "총각김치", "열무김치", "백김치", "파김치", "김치"]),
    ("차", ["녹차", "홍차", "보리차", "옥수수차", "허브차", "차"]),
    ("커피", ["에스프레소", "아메리카노", "라떼", "카푸치노", "콜드브루", "커피"]),
    ("두부", ["연두부", "순두부", "부침두부", "찌개두부", "두부"]),
    ("새우", ["흰다리새우", "대하", "왕새우", "타이거새우", "블랙타이거", "보리새우", "꽃새우", "단새우", "북방새우", "칵테일새우", "냉동새우", "생새우", "껍질새우", "깐새우", "건새우", "마른새우", "새우살", "다진새우", "민물새우", "토하", "크릴", "새우"]),
    ("초콜릿", ["다크초콜릿", "밀크초콜릿", "화이트초콜릿", "가나슈", "초콜릿"]),
)


def _name_contains_nonfood_fragment(name: str) -> bool:
    compact = re.sub(r"\s+", "", name)
    for frag in sorted(_NONFOOD_NAME_FRAGMENTS, key=len, reverse=True):
        if frag in compact:
            return True
    return False


def _collapse_repeated_chunk(s: str) -> str:
    """같은 문자열이 이어붙인 경우 한 번만 남김 (예: 새우새우새우 → 새우)."""
    s = s.strip()
    n = len(s)
    if n < 2:
        return s
    for period in range(1, n // 2 + 1):
        if n % period != 0:
            continue
        chunk = s[:period]
        if chunk * (n // period) == s:
            return chunk
    return s


def _normalize_ingredient_segment(seg: str) -> str:
    seg = seg.strip()
    if not seg:
        return ""
    parts_ws = seg.split()
    if len(parts_ws) > 1 and len(set(parts_ws)) == 1:
        seg = parts_ws[0]
    return _collapse_repeated_chunk(seg)


def _canonicalize_ingredient_name(name: str) -> str:
    """normalizedName 저장용 표준화."""
    s = (name or "").strip()
    if not s:
        return s
    compact = re.sub(r"\s+", "", s)
    for canon, keys in _NORMALIZE_KEYWORD_RULES:
        all_keys = [canon] + list(keys)
        for kw in sorted(all_keys, key=len, reverse=True):
            if kw and kw in compact:
                return canon
    return s


def _equivalent_search_terms(name: str) -> list[str]:
    """검색 시 동의어/변형명을 함께 조회하기 위한 키 목록."""
    s = (name or "").strip()
    if not s:
        return []
    canon = _canonicalize_ingredient_name(s)
    terms = {s, canon}
    for c, keys in _NORMALIZE_KEYWORD_RULES:
        if c == canon:
            terms.update(keys)
            break
    return sorted([t for t in terms if t], key=len, reverse=True)


class FridgeService:
    @staticmethod
    def normalize_ingredient_name_for_query(raw):
        """
        검색·등록 공통: 쉼표/세미콜론으로 반복 나열 축약, 붙여 쓴 반복 축약.
        Returns:
            (정규화된 재료명, None) 또는 (None, 에러 메시지)
        """
        if raw is None:
            return None, "재료명을 입력해주세요."
        s = str(raw).strip()
        if not s:
            return None, "재료명을 입력해주세요."
        # 이 함수는 "단일 재료명" 전용입니다. 콤마 입력은 reject.
        if "," in s:
            return None, "한 번에 하나의 재료만 검색할 수 있습니다."
        # 한글만 허용
        if not re.fullmatch(r"^[\uAC00-\uD7A3]+$", s):
            return None, "재료명은 한글만 입력해주세요."

        name = _normalize_ingredient_segment(s)
        return name, None

    @staticmethod
    def _validate_ingredient_name_core(name: str):
        """정규화된 단일 재료명에 대한 형식·의미 검사."""
        if not name:
            return False, "재료명을 입력해주세요."
        if len(name) > 40:
            return False, "재료명은 40글자 이내로 입력해주세요."
        if not _INGREDIENT_NAME_PATTERN.match(name):
            return False, "재료명은 한글·영문과 일부 기호( · , . ( ) )만 사용할 수 있습니다."
        if re.fullmatch(r"[\d\s]+", name):
            return False, "숫자만으로는 재료명으로 등록할 수 없습니다."
        if not re.search(r"[\uAC00-\uD7A3a-zA-Z]", name):
            return False, "재료명에 글자(한글 또는 영문)를 포함해주세요."
        if _name_contains_nonfood_fragment(name):
            return False, "올바른 재료명을 입력하세요"
        return True, ""

    @staticmethod
    def validate_ingredient_name(raw):
        """재료명 정규화 후 형식·의미 검사. (ok, message, normalized_name)"""
        norm, nerr = FridgeService.normalize_ingredient_name_for_query(raw)
        if nerr:
            return False, nerr, None
        ok, err = FridgeService._validate_ingredient_name_core(norm)
        if not ok:
            return False, err, None
        return True, "", norm

    @staticmethod
    def parse_ingredient_list_for_query(raw):
        """
        쉼표/세미콜론으로 구분된 여러 재료명을 파싱해,
        각 토큰을 반복 축약(새우새우새우->새우) + 숫자 금지 + 의미 검증까지 통과한
        canonical 이름 리스트로 반환합니다.
        """
        if raw is None:
            return None, "재료명을 입력해주세요."
        s = str(raw).strip()
        if not s:
            return None, "재료명을 입력해주세요."

        # 허용: 한글 + ASCII 콤마(,) + 콤마 전후 공백(선택)
        # 예: "당근,버터", "당근, 버터" 허용 / "당근 버터", "당근;버터", "당근，버터" 불허
        if not re.fullmatch(r"^[\uAC00-\uD7A3]+(\s*,\s*[\uAC00-\uD7A3]+)*$", s):
            return None, "재료명은 한글과 ','만 입력할 수 있습니다."

        parts = re.split(r"\s*,\s*", s)
        tokens: list[str] = []
        seen: set[str] = set()
        for p in parts:
            seg = _normalize_ingredient_segment(p)
            if not seg:
                continue
            ok, err = FridgeService._validate_ingredient_name_core(seg)
            if not ok:
                return None, err
            if seg not in seen:
                seen.add(seg)
                tokens.append(seg)

        if not tokens:
            return None, "재료명을 입력해주세요."
        return tokens, None

    @staticmethod
    def infer_category_from_name(raw):
        """재료명 부분 문자열 매칭으로 분류 추정. 없으면 기타."""
        if not raw or not str(raw).strip():
            return "기타"
        name = str(raw).strip()
        nl = name.casefold()
        for cat, keys in _CATEGORY_KEYWORD_RULES:
            for kw in sorted(keys, key=len, reverse=True):
                if kw.casefold() in nl:
                    return cat if cat in ALLOWED_INGREDIENT_CATEGORIES else "기타"
        return "기타"

    @staticmethod
    def _normalize_category(raw):
        if raw is None:
            return "기타"
        s = str(raw).strip()
        return s if s in ALLOWED_INGREDIENT_CATEGORIES else "기타"

    @staticmethod
    def iter_rcp_parts_segments(rcp_parts_dtls: str):
        """레시피 상세와 동일: RCP_PARTS_DTLS를 쉼표·파이프·줄바꿈 단위로 자르고 첫 공백으로 이름/수량 분리."""
        if not rcp_parts_dtls:
            return
        for part in re.split(r"[,|\n]", rcp_parts_dtls):
            raw = part.strip()
            if not raw:
                continue
            name_parts = raw.split(" ", 1)
            name_only = name_parts[0].strip()
            amount = name_parts[1].strip() if len(name_parts) > 1 else ""
            yield name_only, amount

    @staticmethod
    def segment_matches_canonical(name_only: str, canonical: str) -> bool:
        """파싱된 재료 토큰이 사용자가 찾는 재료명과 같은 식재료인지 느슨하게 판별."""
        t = name_only.strip()
        if t[:1] in ("●", "•") and (":" in t or "：" in t):
            parts = re.split(r"[:：]", t, 1)
            if len(parts) == 2 and parts[1].strip():
                t = parts[1].strip()
        first = t.split(" ", 1)[0].strip()
        a = _canonicalize_ingredient_name(first).casefold()
        b = _canonicalize_ingredient_name(canonical).casefold()
        if not a or not b:
            return False
        if a == b:
            return True
        if len(b) >= 2 and b in a:
            return True
        if len(a) >= 2 and a in b:
            return True
        return False

    @staticmethod
    def _rcp_parts_display_fragment(detail: str) -> str:
        """
        RCP_PARTS_DTLS 조각에서 '재료·용량 · 요리명' 형태일 때 앞부분만 남김.
        (요리명/설명은 공공데이터에 중점(·/・/ㆍ) 뒤에 붙는 경우가 많음.)
        """
        if not detail:
            return ""
        s = str(detail).strip()
        s = re.split(r"\s*[·・ㆍ]\s*", s, maxsplit=1)[0].strip()
        return s

    @staticmethod
    def line_matches_canonical(name_only: str, amount: str, canonical: str) -> bool:
        """첫 토큰이 섹션 헤더(●주재료 :)만 있고 실제 재료명이 amount 쪽에 붙은 경우까지 감안."""
        if FridgeService.segment_matches_canonical(name_only, canonical):
            return True
        if amount:
            rest = amount.lstrip(":：").strip()
            if rest:
                head = re.split(r"[,，]", rest, 1)[0].strip()
                if head and FridgeService.segment_matches_canonical(head, canonical):
                    return True
        return False

    @staticmethod
    def search_product_lines_from_recipes(
        canonical_name: str, max_recipes: int = 120, max_results: int = 24
    ):
        """
        foodRecipes.RCP_PARTS_DTLS 텍스트에서 canonical_name에 해당하는 재료 줄을 모은다.
        (레시피 상세 파싱 규칙과 같은 방식으로 줄 단위 후보를 만든 뒤 이름만 매칭.)
        """
        from app.models.recipe import Recipe

        cn = (canonical_name or "").strip()
        if not cn:
            return []
        from sqlalchemy import or_
        terms = _equivalent_search_terms(cn)
        if not terms:
            return []
        like_filters = []
        for t in terms:
            esc = t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            like_filters.append(Recipe.rcpPartsDtls.like(f"%{esc}%", escape="\\"))
        recipes = (
            Recipe.query.filter(
                Recipe.rcpPartsDtls.isnot(None),
                Recipe.rcpPartsDtls != "",
                or_(*like_filters),
            )
            .limit(max_recipes)
            .all()
        )
        out = []
        seen = set()
        for r in recipes:
            for name_only, amount in FridgeService.iter_rcp_parts_segments(r.rcpPartsDtls or ""):
                if not FridgeService.line_matches_canonical(name_only, amount, cn):
                    continue
                detail = (name_only + " " + amount).strip()
                if name_only[:1] in ("●", "•") and amount and amount.lstrip(":：").strip():
                    detail = amount.lstrip(":：").strip()
                display = FridgeService._rcp_parts_display_fragment(detail)
                if not display:
                    continue
                key = (r.rcpSeq, display)
                if key in seen:
                    continue
                seen.add(key)
                out.append(
                    {
                        "recipe_id": r.rcpSeq,
                        "raw_line_name": name_only,
                        "amount_detail": display,
                    }
                )
                if len(out) >= max_results:
                    return out
        return out

    @staticmethod
    def get_user_ingredients(user_id):
        """특정 사용자의 냉장고 재료 목록을 유통기한 임박 순으로 조회합니다."""
        # user_id -> userID, expire_date -> expireDate
        return UserIngredient.query.filter_by(userID=user_id).order_by(UserIngredient.expireDate.asc()).all()

    @staticmethod
    def add_ingredient(
        user_id,
        ingredient_name,
        expire_date_str=None,
        category=None,
        amounts: int = 1,
    ):
        """냉장고에 재료를 추가합니다. (중복 시 amounts 누적)"""
        if not ingredient_name:
            return False, "재료명을 입력해주세요."

        ok_name, name_err, norm_name = FridgeService.validate_ingredient_name(ingredient_name)
        if not ok_name:
            return False, name_err

        # 유통기한 미입력 시: 현재 + 7
        if expire_date_str:
            try:
                expire_date = datetime.strptime(str(expire_date_str), "%Y-%m-%d").date()
            except ValueError:
                return False, "유통기한은 YYYY-MM-DD 형식이어야 합니다."
            if expire_date < date.today():
                return False, "유통기한은 오늘 이후로 설정해주세요."
        else:
            expire_date = date.today() + timedelta(days=7)

        amounts_i = int(amounts) if amounts is not None else 1
        if amounts_i < 1:
            amounts_i = 1

        display_name = str(ingredient_name).strip()
        normalized_name = _canonicalize_ingredient_name(norm_name)
        if category is None or str(category).strip() == "":
            cat = FridgeService.infer_category_from_name(norm_name)
        else:
            cat = FridgeService._normalize_category(category)

        # 팀원의 인메모리 인증으로 인해 DB users 테이블에 사용자가 없을 경우 외래키 에러 방지
        from sqlalchemy import text
        try:
            db.session.execute(
                text("INSERT IGNORE INTO users (ID, userName, passwordHash, nickName) VALUES (:id, :un, :pw, :nn)"),
                {"id": user_id, "un": f"user_{user_id}", "pw": "dummy_hash", "nn": f"User {user_id}"},
            )
            db.session.commit()
        except Exception:
            db.session.rollback()

        try:
            # 같은 userID + normalizedName + expireDate면 amounts 누적
            updated = db.session.execute(
                text(
                    "UPDATE userIngredients "
                    "SET amounts = amounts + :amt, ingredientName = :name, category = :cat "
                    "WHERE userID = :uid AND normalizedName = :norm AND expireDate = :exp"
                ),
                {
                    "amt": amounts_i,
                    "name": display_name,
                    "cat": cat,
                    "uid": user_id,
                    "norm": normalized_name,
                    "exp": expire_date,
                },
            )
            rowcount = getattr(updated, "rowcount", 0) or 0

            if rowcount <= 0:
                db.session.execute(
                    text(
                        "INSERT INTO userIngredients "
                        "(userID, ingredientName, normalizedName, expireDate, category, amounts) "
                        "VALUES (:uid, :name, :norm, :exp, :cat, :amt)"
                    ),
                    {
                        "uid": user_id,
                        "name": display_name,
                        "norm": normalized_name,
                        "exp": expire_date,
                        "cat": cat,
                        "amt": amounts_i,
                    },
                )

            db.session.commit()

            # 누적/신규 모두 동일 키로 최신 레코드 조회
            new_item = (
                UserIngredient.query.filter_by(
                    userID=user_id,
                    normalizedName=normalized_name,
                    expireDate=expire_date,
                )
                .order_by(UserIngredient.ID.desc())
                .first()
            )
            return True, new_item
        except Exception as e:
            db.session.rollback()
            return False, f"데이터베이스 저장 오류: {str(e)}"

    @staticmethod
    def edit_ingredient(user_id, ingredient_id, ingredient_name, expire_date_str, category=_CATEGORY_OMITTED):
        """냉장고 재료 정보를 수정합니다."""
        # id -> ID, user_id -> userID
        item = UserIngredient.query.filter_by(ID=ingredient_id, userID=user_id).first()
        if not item:
            return False, "해당 재료를 찾을 수 없습니다."
            
        if not ingredient_name or not expire_date_str:
            return False, "재료명과 유통기한을 모두 입력해주세요."

        ok_name, name_err, norm_name = FridgeService.validate_ingredient_name(ingredient_name)
        if not ok_name:
            return False, name_err

        try:
            expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
        except ValueError:
            return False, "유통기한은 YYYY-MM-DD 형식이어야 합니다."
        if expire_date < date.today():
            return False, "유통기한은 오늘 이후로 설정해주세요."

        if category is _CATEGORY_OMITTED:
            cat = FridgeService._normalize_category(item.category)
        else:
            cat = FridgeService._normalize_category(category)

        norm_for_db = _canonicalize_ingredient_name(norm_name)
        # 모델 속성 업데이트 (카멜 케이스)
        try:
            from sqlalchemy import text
            db.session.execute(
                text(
                    "UPDATE userIngredients SET ingredientName = :name, normalizedName = :norm, expireDate = :exp, category = :cat "
                    "WHERE ID = :id AND userID = :uid"
                ),
                {
                    "name": str(ingredient_name).strip(),
                    "norm": norm_for_db,
                    "exp": expire_date,
                    "cat": cat,
                    "id": ingredient_id,
                    "uid": user_id,
                },
            )
            db.session.commit()
            
            # 수정된 항목 다시 조회
            updated_item = UserIngredient.query.filter_by(ID=ingredient_id, userID=user_id).first()
            return True, updated_item
        except Exception as e:
            db.session.rollback()
            return False, f"데이터베이스 저장 오류: {str(e)}"

    @staticmethod
    def delete_ingredient(user_id, ingredient_id):
        """냉장고에서 특정 재료를 삭제합니다."""
        # id -> ID, user_id -> userID
        item = UserIngredient.query.filter_by(ID=ingredient_id, userID=user_id).first()
        if not item:
            return False, "해당 재료를 찾을 수 없거나 삭제 권한이 없습니다."
            
        try:
            from sqlalchemy import text
            db.session.execute(text("DELETE FROM userIngredients WHERE ID = :id AND userID = :uid"), {"id": ingredient_id, "uid": user_id})
            db.session.commit()
            return True, "삭제 완료"
        except Exception as e:
            db.session.rollback()
            return False, f"데이터베이스 삭제 오류: {str(e)}"
    @staticmethod
    def clean_ingredient_name(raw_text):
        """괄호 내용과 콤마 잔해까지 싹 지우는 최종 병기 정제 로직"""
        if not raw_text: return ""
        
        # 1. HTML 태그 제거 (<br> 등)
        text = re.sub(r'<.*?>', ' ', raw_text)
        
        # 2. 대괄호 내용 제거 ([가정간편식] 등)
        text = re.sub(r'\[.*?\]', ' ', text)
        
        # 3. 🎯 핵심: 괄호와 그 안의 내용 통째로 제거! 
        # (통삼겹살 , ) 이런 거 고민하지 말고 그냥 괄호 자체를 날립니다.
        text = re.sub(r'\(.*?\)', ' ', text)
        
        # 4. 숫자와 단위 제거 (600g, 1개 등)
        text = re.sub(r'[\d\./]+[gml|개|봉지|큰술|작은술|컵|가닥|cm|장|마리|쪽|알]*', ' ', text)
        
        # 5. 불필요한 특수기호 및 콤마 제거
        # 🎯 콤마(,)와 마침표(.)도 여기서 지워버립니다.
        text = re.sub(r'[●:•\-\[\],.]', ' ', text)
        
        # 6. 양끝 공백 제거 및 중간 중복 공백 하나로 합치기
        text = " ".join(text.split())
        
        return text.strip()

    @staticmethod
    def get_standard_name(ingredient_name):
        """DB의 ingredientAlias 테이블을 참조하여 표준명 반환"""
        clean_name = FridgeService.clean_ingredient_name(ingredient_name)
        # 🎯 SQL 실행 시 에러 방지를 위해 try-except 추가
        try:
            query = text("SELECT standardName FROM ingredientAlias WHERE aliasName = :name")
            result = db.session.execute(query, {"name": clean_name}).fetchone()
            return result[0] if result else clean_name
        except Exception as e:
            print(f"[Alias DB Error] {e}")
            return clean_name

    @staticmethod
    def get_recommended_recipes(user_id):
        EXCLUDE_INGREDIENTS = {
            # 1. 시스템 단어 (가장 킹받는 부분)
            "기준", "재료", "주재료", "부재료", "양념", "소스", "고명", "선택", "준비", "약간",
            "인분", "인분기준", "내용물", "함량", "구성", "추가", "가정간편식",
            
            # 2. 양념/가루/기본 재료 (사러 갈 필요 없는 것들)
            "소금", "설탕", "후추", "후춧가루", "고춧가루", "밀가루", "녹말가루", "전분", 
            "식용유", "참기름", "들기름", "올리브유", "간장", "진간장", "국간장", "저염간장", 
            "다진마늘", "마늘", "생강", "맛술", "청주", "물", "육수", "통깨", "깨",
            "올리고당", "물엿", "식초", "케찹", "마요네즈", "고추장", "된장"
        }
        """유통기한 임박 재료 기반 + 별칭 매칭 추천 로직"""
        try:
            # 1. 내 냉장고 재료 가져오기 (컬럼명 userID, ingredientName 확인!)
            all_user_items = UserIngredient.query.filter_by(userID=user_id).all()
            
            # 🎯 중요: FridgeService 내부의 메서드를 호출해야 함 (ApiService X)
            owned_standard_set = {FridgeService.get_standard_name(item.ingredientName) for item in all_user_items}
            print(f"🔎 내 냉장고 표준화 재료: {owned_standard_set}")
            
            if not owned_standard_set:
                return []
            
            # 2. 유통기한 임박 재료 2개 추출
            urgent_items = UserIngredient.query.filter_by(userID=user_id)\
                .order_by(UserIngredient.expireDate.asc()).all()
            
            search_keywords = []
            for item in urgent_items:
                std_name = FridgeService.get_standard_name(item.ingredientName)
                if std_name not in search_keywords:
                    search_keywords.append(std_name)
                if len(search_keywords) >= 3: break
            
            search_query = ",".join(search_keywords)
            print(f"🚀 최종 API 검색 키워드: {search_query}")

            # 3. 공공 API 호출
            api_key = "3601fcadc33549809411"
            url = f"https://openapi.foodsafetykorea.go.kr/api/{api_key}/COOKRCP01/json/1/10/RCP_PARTS_DTLS={search_query}"
            
            response = requests.get(url, timeout=5)
            data = response.json()
            
            recommended = []
            if "COOKRCP01" in data and "row" in data["COOKRCP01"]:
                for r in data["COOKRCP01"]["row"]:
                    raw_parts = r.get("RCP_PARTS_DTLS", "")
                    
                    # 🎯 [중요] 괄호와 노이즈를 먼저 제거 (아까 말씀드린 순서!)
                    cleaned_full_text = FridgeService.clean_ingredient_name(raw_parts)
                    
                    # 🎯 [중요] 공백이나 콤마 등으로 쪼개기
                    parts_list = re.split(r'[,\s]+', cleaned_full_text)
                    
                    have_ingr = []
                    missing_ingr = []
                    
                    for p in parts_list:
                        p_clean = p.strip()
                        # 글자 수가 1글자이거나(예: '중', '대'), 필터링 리스트에 있으면 제외
                        if not p_clean or len(p_clean) < 2 or p_clean in EXCLUDE_INGREDIENTS: 
                            continue
                        
                        recipe_std_name = FridgeService.get_standard_name(p_clean)
                        
                        # 표준명으로 변환 후에도 필터링 리스트에 있는지 한 번 더 체크
                        if recipe_std_name in EXCLUDE_INGREDIENTS:
                            continue

                        if recipe_std_name in owned_standard_set:
                            if p_clean not in have_ingr:
                                have_ingr.append(p_clean)
                        else:
                            # 🎯 부족 재료 목록에 넣기 전 최종 검사
                            if p_clean not in missing_ingr:
                                missing_ingr.append(p_clean)

                    total = len(have_ingr) + len(missing_ingr)
                    match_percent = int((len(have_ingr) / total) * 100) if total > 0 else 0

                    # 🎯 HTML(recommend.html)의 변수명과 100% 일치시켜야 함
                    recommended.append({
                        "recipeID": r.get("RCP_SEQ"),
                        "RCP_NM": r.get("RCP_NM"),
                        "ATT_FILE_NO_MAIN": r.get("ATT_FILE_NO_MAIN") or "/static/images/default_recipe.jpg",
                        "description": f"{r.get('RCP_WAY2')} | {r.get('RCP_PAT2')}",
                        "haveIngredients": have_ingr,
                        "missingIngredients": missing_ingr,
                        "matchPercent": match_percent
                    })
                recommended.sort(key=lambda x: (len(x['missingIngredients']), -x['matchPercent']))
                print(f"✅ 추천 레시피 {len(recommended)}개 추출 성공")
                return recommended
            
            print("❌ API에서 가져온 레시피 데이터가 없습니다.")
            return []

        except Exception as e:
            print(f"🚨 [Recommend Logic Error] {e}")
            return []