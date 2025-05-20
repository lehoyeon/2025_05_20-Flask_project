# 사전 설치 : pip install flask pymysql
from flask import Flask, render_template, request, redirect, url_for, jsonify
from db import Database
import atexit   # 애플리케이션 종료시 실행을 요청 (ex. DB연결 종료)

app = Flask(__name__)   # Flask 앱 초기화
db = Database()   # DB 초기화
conn = db.connection
cursor = conn.cursor()


@app.route('/registration')
def index():
    return render_template('registration.html')  # HTML 파일 이름
@app.route('/user')
def users_page():
    return render_template('user.html')
# ------------------ 사용자 관련 ------------------

@app.route('/users', methods=['POST'])
def create_user():
    name = request.json.get('name')
    if not name:
        return jsonify({'error': '이름을 입력하세요'}), 400
    cursor.execute("INSERT INTO users (name) VALUES (%s)", (name,))
    conn.commit()
    return jsonify({'message': '사용자 등록 완료'}), 201

@app.route('/users', methods=['GET'])
def get_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    new_name = request.json.get('name')
    cursor.execute("UPDATE users SET name = %s WHERE user_id = %s", (new_name, user_id))
    conn.commit()
    return jsonify({'message': '사용자 정보 수정 완료'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    return jsonify({'message': '사용자 삭제 완료'})

# ------------------ 물품 관련 ------------------

@app.route('/items', methods=['POST'])
def create_item():
    data = request.json
    name = data.get('name')
    price = data.get('price')
    quantity = data.get('quantity', 1)

    if not name or price is None:
        return jsonify({'error': '이름과 가격은 필수입니다'}), 400

    cursor.execute(
        "INSERT INTO items (name, price, quantity) VALUES (%s, %s, %s)",
        (name, price, quantity)
    )
    conn.commit()
    return jsonify({'message': '물품 등록 완료'}), 201

@app.route('/items', methods=['GET'])
def get_items():
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    return jsonify(items)

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    name = data.get('name')
    price = data.get('price')
    quantity = data.get('quantity')

    cursor.execute(
        "UPDATE items SET name = %s, price = %s, quantity = %s WHERE item_id = %s",
        (name, price, quantity, item_id)
    )
    conn.commit()
    return jsonify({'message': '물품 수정 완료'})

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    cursor.execute("DELETE FROM items WHERE item_id = %s", (item_id,))
    conn.commit()
    return jsonify({'message': '물품 삭제 완료'})



import atexit
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

# ------------------ 종료 시 DB 연결 닫기 ------------------
import atexit
atexit.register(db.close)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)