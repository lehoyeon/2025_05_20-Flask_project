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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)