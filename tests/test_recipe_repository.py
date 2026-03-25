"""
########################################################################################
# 파일명: test_recipe_repository.py
# 목적: SQLAlchemy의 Recipe 모델이 MariaDB와 정상적으로 연동되는지 확인하는 테스트 파일입니다.
# 
# 테스트 내용:
#   - 특정 RCP_SEQ(기본키)로 조회 시 데이터베이스 레코드를 성공적으로 가져오는지 검증
#   - 반환된 객체가 올바른 SQLAlchemy 모델(Recipe) 인스턴스인지 확인
#   - 동적으로 생성되는 매뉴얼(manual01 등) 데이터가 존재하는지 검증
#
# 실행 방법:
#   python -m unittest tests/test_recipe_repository.py
#
# 발생 가능한 오류 및 예외 처리:
#   - AssertionError: 기대하는 데이터(RCP_NM 등)가 누락되었거나 ID가 일치하지 않을 때 발생
#   - Database Error: MariaDB 서버가 꺼져 있거나 Config 설정이 올바르지 않으면 연결 실패
########################################################################################
"""
import unittest
import os
import sys

# 프로젝트 최상단 디렉토리를 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.foodRecipes import Recipe

class TestRecipeModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """모든 테스트 실행 전 Flask 앱 컨텍스트 설정."""
        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    def test_recipe_model_fetches_valid_data(self):
        """Recipe 모델이 MariaDB에서 레코드를 제대로 가져오는지 테스트 및 검증합니다."""
        valid_id = 18
        
        # Act: SQLAlchemy를 사용하여 레시피 가져오기
        recipe = db.session.get(Recipe, valid_id)
        
        # Assert: 레시피 객체가 존재하는지 확인
        self.assertIsNotNone(recipe, f"ID가 {valid_id}인 레시피를 가져오지 못했습니다.")
        self.assertIsInstance(recipe, Recipe, "결과값은 Recipe 모델의 인스턴스여야 합니다.")
        
        # Assert: 레시피 ID와 기본 항목 매핑 확인
        self.assertEqual(recipe.rcpSeq, valid_id, f"rcpSeq 값은 {valid_id}와 일치해야 합니다.")
        self.assertTrue(hasattr(recipe, 'rcpNm'), "기대하는 속성이 누락되었습니다: rcpNm")
        self.assertTrue(hasattr(recipe, 'rcpWay2'), "기대하는 속성이 누락되었습니다: rcpWay2")
        
        # Assert: 매뉴얼 텍스트 데이터가 채워져 있는지 확인 (01 ~ 20)
        self.assertIsNotNone(recipe.manual01, "MANUAL01 데이터가 존재하지 않습니다.")
        
        print(f"검증 완료: SQLAlchemy 모델을 통해 레시피 '{recipe.rcpNm}' 조회에 성공했습니다.")

    @classmethod
    def tearDownClass(cls):
        """테스트 종료 후 앱 컨텍스트 정리."""
        cls.app_context.pop()

if __name__ == '__main__':
    unittest.main()
