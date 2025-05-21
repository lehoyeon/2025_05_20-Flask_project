import pymysql
from pymysql import Error
from rentalResult import RentalStats

class Database:
    def __init__(self):
        self.connection = None
        try:
            self.connection = pymysql.connect(
                host='192.168.0.30',
                database='flask',  
                user='root',
                password='user1234',  # mariadb 설치 당시의 패스워드, 실제 환경에서는 보안을 위해 환경변수 등을 사용
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print("MariaDB에 성공적으로 연결되었습니다.")
        except Error as e:
            print(f"MariaDB 연결 중 오류 발생: {e}")

    def close(self):
        """데이터베이스 연결 종료"""
        if self.connection:
            self.connection.close()
            print("MariaDB 연결이 종료되었습니다.")
            
    @staticmethod
    def fetch_rental_performance():
        """전체 대여 실적 데이터를 가져옵니다"""
        db = Database()
        result = RentalStats.fetch_rental_performance(db.connection)
        db.close()
        return result
        
    @staticmethod
    def fetch_monthly_stats():
        """월별 통계 데이터를 가져옵니다"""
        db = Database()
        result = RentalStats.fetch_monthly_stats(db.connection)
        db.close()
        return result
        
    @staticmethod
    def get_top_users(limit=5):
        """상위 사용자 데이터를 가져옵니다"""
        db = Database()
        result = RentalStats.get_top_users(db.connection, limit)
        db.close()
        return result
        
    @staticmethod
    def get_top_items(limit=5):
        """상위 물품 데이터를 가져옵니다"""
        db = Database()
        result = RentalStats.get_top_items(db.connection, limit)
        db.close()
        return result