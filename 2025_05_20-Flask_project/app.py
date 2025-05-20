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
    # 예시 데이터
    total_rentals = 120
    total_revenue = 350000
    user_stats = [
        {'username': '홍길동', 'rental_count': 10, 'total_amount': 50000},
        {'username': '김철수', 'rental_count': 7, 'total_amount': 35000},
    ]
    item_stats = [
        {'item_name': '노트북', 'rental_count': 15, 'total_revenue': 150000},
        {'item_name': '빔프로젝터', 'rental_count': 8, 'total_revenue': 80000},
    ]
    return render_template('status.html',
                           total_rentals=total_rentals,
                           total_revenue=total_revenue,
                           user_stats=user_stats,
                           item_stats=item_stats)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)