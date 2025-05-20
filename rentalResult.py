import pymysql
from pymysql import Error

class RentalStats:
    @staticmethod
    def fetch_rental_performance(connection):
        """
        Fetches comprehensive rental statistics from the database
        
        Args:
            connection: Active database connection
            
        Returns:
            dict: Dictionary containing all rental statistics or None if error
        """
        if not connection:
            return None
            
        try:
            with connection.cursor() as cursor:
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

    @staticmethod
    def fetch_monthly_stats(connection):
        """
        Fetches monthly rental statistics for chart visualization
        
        Args:
            connection: Active database connection
            
        Returns:
            list: List of monthly statistics or None if error
        """
        if not connection:
            return None
            
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        DATE_FORMAT(rent_date, '%Y-%m') AS month,
                        COUNT(*) AS rental_count,
                        COALESCE(SUM(price), 0) AS total_revenue
                    FROM rentals
                    GROUP BY DATE_FORMAT(rent_date, '%Y-%m')
                    ORDER BY month
                """)
                return cursor.fetchall()
        except Error as e:
            print(f"월별 통계 조회 중 오류 발생: {e}")
            return None
            
    @staticmethod
    def get_top_users(connection, limit=5):
        """
        Fetches top users by rental amount
        
        Args:
            connection: Active database connection
            limit: Number of top users to return
            
        Returns:
            list: List of top users or None if error
        """
        if not connection:
            return None
            
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        u.name AS username,
                        COUNT(r.rental_id) AS rental_count,
                        COALESCE(SUM(r.price), 0) AS total_amount
                    FROM users u
                    JOIN rentals r ON u.user_id = r.user_id
                    GROUP BY u.user_id, u.name
                    ORDER BY total_amount DESC
                    LIMIT %s
                """, (limit,))
                return cursor.fetchall()
        except Error as e:
            print(f"상위 사용자 조회 중 오류 발생: {e}")
            return None
            
    @staticmethod
    def get_top_items(connection, limit=5):
        """
        Fetches top items by rental revenue
        
        Args:
            connection: Active database connection
            limit: Number of top items to return
            
        Returns:
            list: List of top items or None if error
        """
        if not connection:
            return None
            
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        i.name AS item_name,
                        COUNT(r.rental_id) AS rental_count,
                        COALESCE(SUM(r.price), 0) AS total_revenue
                    FROM items i
                    JOIN rentals r ON i.item_id = r.item_id
                    GROUP BY i.item_id, i.name
                    ORDER BY total_revenue DESC
                    LIMIT %s
                """, (limit,))
                return cursor.fetchall()
        except Error as e:
            print(f"상위 물품 조회 중 오류 발생: {e}")
            return None
