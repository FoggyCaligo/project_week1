"""
########################################################################################
# 파일명: recipeDetailRepository.py
# 목적: MariaDB의 'foodRecipes' 테이블과 직접 통신하여 원본 데이터를 가져오는 
#       데이터 액세스 레이어(Repository)입니다.
# 
# 입력:   recipe_id (int) - 데이터베이스의 RCP_SEQ 값 (예: 18)
# 출력:   - 단일 레시피 조회 시: 55개의 컬럼을 포함한 딕셔너리
#         - 목록 조회 시: 여러 개의 레시피 정보를 담은 리스트
#
# 사용 방법:
#   from db import Database
#   from repository.recipeDetailRepository import RecipeDetailRepository
#
#   db = Database()
#   repo = RecipeDetailRepository(db)
#   raw_data = repo.get_recipe_details(18)
########################################################################################
"""
import pymysql

class RecipeDetailRepository:
    def __init__(self, db):
        """
        db: An instance of the Database class from db.py
        """
        self.db = db

    def get_recipe_details(self, recipe_id):
        """Fetches ALL available information from foodRecipes for one recipe."""
        if not self.db.connection:
            return None
        
        try:
            with self.db.connection.cursor() as cursor:
                # Use SELECT * to get all 55 columns (including all steps and images)
                sql = "SELECT * FROM foodRecipes WHERE RCP_SEQ = %s"
                cursor.execute(sql, (recipe_id,))
                return cursor.fetchone()
        except pymysql.Error as e:
            print(f"Error fetching recipe details: {e}")
            return None

    def get_all_recipes(self, limit=10):
        """Fetches a list of recipes from the table."""
        if not self.db.connection:
            return []
        
        try:
            with self.db.connection.cursor() as cursor:
                sql = "SELECT * FROM foodRecipes LIMIT %s"
                cursor.execute(sql, (limit,))
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error fetching recipe list: {e}")
            return []
###
    def get_ingredients(self, recipe_id):
        """Fetches ingredients for a specific recipe."""
        if not self.db.connection:
            return []
        
        try:
            with self.db.connection.cursor() as cursor:
                # Assuming 'recipe_ingredients' table joins 'recipes' and 'ingredients'
                sql = """
                SELECT 
                    name, 
                    amount 
                FROM recipe_ingredients 
                WHERE recipe_id = %s
                ORDER BY id ASC
                """
                cursor.execute(sql, (recipe_id,))
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error fetching recipe ingredients: {e}")
            return []

    def get_steps(self, recipe_id):
        """Fetches cooking steps for a specific recipe."""
        if not self.db.connection:
            return []
        
        try:
            with self.db.connection.cursor() as cursor:
                sql = """
                SELECT 
                    step_number, 
                    title, 
                    description, 
                    image_url AS imageUrl 
                FROM recipe_steps 
                WHERE recipe_id = %s 
                ORDER BY step_number ASC
                """
                cursor.execute(sql, (recipe_id,))
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error fetching recipe steps: {e}")
            return []

    def get_nutrition(self, recipe_id):
        """Fetches nutrition facts for a specific recipe."""
        if not self.db.connection:
            return None
        
        try:
            with self.db.connection.cursor() as cursor:
                sql = """
                SELECT 
                    carbohydrate, 
                    protein, 
                    fat 
                FROM recipe_nutrition 
                WHERE recipe_id = %s
                """
                cursor.execute(sql, (recipe_id,))
                return cursor.fetchone()
        except pymysql.Error as e:
            print(f"Error fetching recipe nutrition: {e}")
            return None
