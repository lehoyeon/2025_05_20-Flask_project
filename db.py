import pymysql
from pymysql import Error

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
            
    def fetch_rental_performance():
        db = Database()
        if not db.connection:
            return None
        try:
            with db.connection.cursor() as cursor:
                # 전체 실적 요약 (총 대여 횟수, 총 수익)
                cursor.execute("""
                    SELECT 
                        COUNT(rental_id) AS total_rentals,
                        COALESCE(SUM(price), 0) AS total_revenue
                    FROM rentals
                """)
                total_summary = cursor.fetchone()

                # 사용자별 실적 (이름, 대여 건수, 총 금액)
                cursor.execute("""
                    SELECT 
                        u.name AS username,
                        COUNT(r.rental_id) AS rental_count,
                        COALESCE(SUM(r.price), 0) AS total_amount
                    FROM users u
                    LEFT JOIN rentals r ON u.user_id = r.user_id
                    GROUP BY u.user_id, u.name
                    ORDER BY total_amount DESC
                """)
                user_stats = cursor.fetchall()

                # 물건별 실적 (물건명, 대여 횟수, 누적 수익)
                cursor.execute("""
                    SELECT 
                        i.name AS item_name,
                        COUNT(r.rental_id) AS rental_count,
                        COALESCE(SUM(r.price), 0) AS total_revenue
                    FROM items i
                    LEFT JOIN rentals r ON i.item_id = r.item_id
                    GROUP BY i.item_id, i.name
                    ORDER BY total_revenue DESC
                """)
                item_stats = cursor.fetchall()

            return {
                'total_rentals': total_summary['total_rentals'],
                'total_revenue': total_summary['total_revenue'],
                'user_stats': user_stats,
                'item_stats': item_stats
            }
        except Error as e:
            print(f"쿼리 실행 중 오류 발생: {e}")
            return None
        finally:
            db.close()
