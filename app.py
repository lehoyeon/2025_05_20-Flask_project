# 사전 설치 : pip install flask pymysql
from flask import Flask, render_template, request, redirect, url_for
from db import Database
import atexit   # 애플리케이션 종료시 실행을 요청 (ex. DB연결 종료)

app = Flask(__name__)   # Flask 앱 초기화
db = Database()   # DB 초기화

# 애플리케이션 종료 시 DB 연결 종료
atexit.register(db.close)

@app.route('/status', methods=['GET'])
def status():
    data = Database.fetch_rental_performance()
    
    if not data:
        return render_template('status.html',
                             total_rentals=0,
                             total_revenue=0,
                             user_stats=[],
                             item_stats=[])

    return render_template('status.html',
                         total_rentals=data['total_rentals'],
                         total_revenue=data['total_revenue'],
                         user_stats=data['user_stats'],
                         item_stats=data['item_stats'])

@app.route('/api/monthly-stats')
def monthly_stats():
    db = Database()
    try:
        with db.connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(rent_date, '%Y-%m') AS month,
                    COUNT(*) AS rental_count,
                    SUM(price) AS total_revenue
                FROM rentals
                GROUP BY DATE_FORMAT(rent_date, '%Y-%m')
                ORDER BY month
            """)
            data = cursor.fetchall()
        return {'success': True, 'data': data}
    except Error as e:
        print(f"Error fetching monthly stats: {e}")
        return {'success': False}
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)