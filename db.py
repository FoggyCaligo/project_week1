import pymysql
import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

class Database():
    def __init__(self):
        self.connection=None
        try:
            # Use os.getenv and provide a default port to avoid errors
            self.connection=pymysql.connect(
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT', 3306)),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print("MariaDB에 성공적으로 연결되었습니다.")
        except pymysql.Error as e:
            print(f"MariaDB 연결 중 오류 발생: {e}")
            
    def close(self):
        """데이터베이스 연결 종료"""
        if self.connection:
            self.connection.close()
            print("MariaDB 연결이 종료되었습니다.")