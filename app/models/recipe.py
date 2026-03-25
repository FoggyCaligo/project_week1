"""
########################################################################################
# 파일명: foodRecipes.py
# 목적: MariaDB의 'foodRecipes' 테이블과 매핑되는 SQLAlchemy ORM 모델입니다.
# 
# 구조 및 내용: 
#   - RCP_SEQ를 기본키(primary_key)로 지정하여 레시피 데이터를 관리합니다.
#   - 각 컬럼은 데이터베이스에 있는 컬럼(예: RCP_NM, INFO_ENG 등)과 정확히 연결됩니다.
#   - 20단계(manual01 ~ 20) 조리과정 및 이미지 컬럼을 포함하고 있습니다.
#
# 사용 방법:
#   from app.models.foodRecipes import Recipe
#   from app import db
#
#   # 레시피 조회 (단건)
#   recipe = db.session.get(Recipe, 18)
#
# 발생 가능한 오류 및 예외 처리:
#   - RuntimeError: Flask 앱에서 SQLAlchemy 초기화(init_app)를 누락했을 경우 발생
#   - SQLAlchemyError: 데이터베이스 연결 실패 또는 존재하지 않는 테이블 조회 시 발생
########################################################################################
"""
from database import db

class Recipe(db.Model):
    # MariaDB의 테이블명과 정확히 일치해야 합니다.
    __tablename__ = 'foodRecipes'
    
    
    rcpSeq = db.Column('RCP_SEQ', db.Integer, primary_key=True)
    rcpNm = db.Column('RCP_NM', db.String(255))
    rcpWay2 = db.Column('RCP_WAY2', db.String(50))
    rcpPat2 = db.Column('RCP_PAT2', db.String(50))
    attFileNoMain = db.Column('ATT_FILE_NO_MAIN', db.String(255))
    rcpPartsDtls = db.Column('RCP_PARTS_DTLS', db.Text)
    infoEng = db.Column('INFO_ENG', db.String(50))
    infoCar = db.Column('INFO_CAR', db.String(50))
    infoPro = db.Column('INFO_PRO', db.String(50))
    infoFat = db.Column('INFO_FAT', db.String(50))
    infoNa = db.Column('INFO_NA', db.String(50))

    manual01 = db.Column('MANUAL01', db.String(255))
    manual02 = db.Column('MANUAL02', db.String(255))
    manual03 = db.Column('MANUAL03', db.String(255))
    manual04 = db.Column('MANUAL04', db.String(255))
    manual05 = db.Column('MANUAL05', db.String(255))
    manual06 = db.Column('MANUAL06', db.String(255))
    manual07 = db.Column('MANUAL07', db.String(255))
    manual08 = db.Column('MANUAL08', db.String(255))
    manual09 = db.Column('MANUAL09', db.String(255))
    manual10 = db.Column('MANUAL10', db.String(255))
    manual11 = db.Column('MANUAL11', db.String(255))
    manual12 = db.Column('MANUAL12', db.String(255))
    manual13 = db.Column('MANUAL13', db.String(255))
    manual14 = db.Column('MANUAL14', db.String(255))
    manual15 = db.Column('MANUAL15', db.String(255))
    manual16 = db.Column('MANUAL16', db.String(255))
    manual17 = db.Column('MANUAL17', db.String(255))
    manual18 = db.Column('MANUAL18', db.String(255))
    manual19 = db.Column('MANUAL19', db.String(255))
    manual20 = db.Column('MANUAL20', db.String(255))
    manualImg01 = db.Column('MANUAL_IMG01', db.Text)
    manualImg02 = db.Column('MANUAL_IMG02', db.Text)
    manualImg03 = db.Column('MANUAL_IMG03', db.Text)
    manualImg04 = db.Column('MANUAL_IMG04', db.Text)
    manualImg05 = db.Column('MANUAL_IMG05', db.Text)
    manualImg06 = db.Column('MANUAL_IMG06', db.Text)
    manualImg07 = db.Column('MANUAL_IMG07', db.Text)
    manualImg08 = db.Column('MANUAL_IMG08', db.Text)
    manualImg09 = db.Column('MANUAL_IMG09', db.Text)
    manualImg10 = db.Column('MANUAL_IMG10', db.Text)
    manualImg11 = db.Column('MANUAL_IMG11', db.Text)
    manualImg12 = db.Column('MANUAL_IMG12', db.Text)
    manualImg13 = db.Column('MANUAL_IMG13', db.Text)
    manualImg14 = db.Column('MANUAL_IMG14', db.Text)
    manualImg15 = db.Column('MANUAL_IMG15', db.Text)
    manualImg16 = db.Column('MANUAL_IMG16', db.Text)
    manualImg17 = db.Column('MANUAL_IMG17', db.Text)
    manualImg18 = db.Column('MANUAL_IMG18', db.Text)
    manualImg19 = db.Column('MANUAL_IMG19', db.Text)
    manualImg20 = db.Column('MANUAL_IMG20', db.Text)