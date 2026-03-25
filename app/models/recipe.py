from database import db

class FoodRecipe(db.Model):
    __tablename__ = 'foodRecipes'

    RCP_SEQ = db.Column(db.Integer, primary_key=True, comment='일련번호')
    RCP_NM = db.Column(db.String(255), comment='메뉴명')
    RCP_WAY2 = db.Column(db.String(50), comment='조리방법')
    RCP_PAT2 = db.Column(db.String(50), comment='요리종류')
    INFO_WGT = db.Column(db.String(50), comment='중량(1인분)')
    INFO_ENG = db.Column(db.String(50), comment='열량(kcal)')
    INFO_CAR = db.Column(db.String(50), comment='탄수화물(g)')
    INFO_PRO = db.Column(db.String(50), comment='단백질(g)')
    INFO_FAT = db.Column(db.String(50), comment='지방(g)')
    INFO_NA = db.Column(db.String(50), comment='나트륨(mg)')
    HASH_TAG = db.Column(db.String(255), comment='해쉬태그')
    ATT_FILE_NO_MAIN = db.Column(db.String(255), comment='이미지경로(소)')
    ATT_FILE_NO_MK = db.Column(db.String(255), comment='이미지경로(대)')
    RCP_PARTS_DTLS = db.Column(db.Text, comment='재료정보')
    RCP_NA_TIP = db.Column(db.Text, comment='저감 조리법 TIP')
    
    # 조리 과정 및 이미지 (1~20) 동적 생성
    for i in range(1, 21):
        idx = f"{i:02d}"
        locals()[f'MANUAL{idx}'] = db.Column(db.Text)
        locals()[f'MANUAL_IMG{idx}'] = db.Column(db.String(255))