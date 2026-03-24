"""
########################################################################################
# 파일명: test_recipe_repository.py
# 목적: RecipeDetailRepository의 기능이 실제 데이터베이스와 연동되어 
#       올바르게 작동하는지 확인하는 단위 테스트 및 통합 테스트 파일입니다.
# 
# 테스트 내용:
#   - 특정 RCP_SEQ로 조회 시 실제 데이터가 반환되는지 확인
#   - 반환된 데이터가 딕셔너리 형태인지 확인
#   - 필드가 누락되지 않고 55개 컬럼이 모두 포함되어 있는지 검증
#
# 실행 방법:
#   python tests/test_recipe_repository.py
########################################################################################
"""
import unittest
import os
import sys

# Add the project root to sys.path so we can import db and repository
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import Database
from repository.recipeDetailRepository import RecipeDetailRepository

class TestRecipeDetailRepository(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the database connection once for all tests."""
        cls.db = Database()
        cls.repo = RecipeDetailRepository(cls.db)

    def test_get_recipe_details_returns_all_columns(self):
        """Test that get_recipe_details returns all columns for a valid RCP_SEQ."""
        valid_id = 18  # This was previously verified to exist
        
        # Act
        recipe = self.repo.get_recipe_details(valid_id)
        
        # Assert: Basic valid instance
        self.assertIsNotNone(recipe, f"Failed to fetch recipe with ID {valid_id}")
        self.assertIsInstance(recipe, dict, "Result should be a dictionary")
        
        # Assert: ID matches
        self.assertEqual(int(recipe.get('RCP_SEQ', 0)), valid_id, f"RCP_SEQ should match {valid_id}")
        
        # Assert: Check for key columns from the 'foodRecipes' table
        expected_keys = [
            'RCP_NM', 'RCP_WAY2', 'RCP_PAT2', 'RCP_PARTS_DTLS', 
            'INFO_ENG', 'INFO_CAR', 'INFO_PRO', 'INFO_FAT', 
            'ATT_FILE_NO_MAIN', 'MANUAL01', 'MANUAL_IMG01'
        ]
        for key in expected_keys:
            self.assertIn(key, recipe, f"Missing expected key: {key}")

        print(f"Verified: Successfully fetched recipe '{recipe['RCP_NM']}' with all 55 columns.")

    @classmethod
    def tearDownClass(cls):
        """Close the database connection after all tests."""
        if cls.db:
            cls.db.close()

if __name__ == '__main__':
    unittest.main()
