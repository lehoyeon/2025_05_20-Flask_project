from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from datetime import datetime
import pandas as pd       # DataFrame 및 엑셀 저장용
import io                 # 메모리 버퍼에 엑셀을 저장하기 위함
from db import Database   # 사용자 정의 DB 연결 클래스

app = Flask(__name__)
db = Database()

#반납 아이템 목록
@app.route('/return_item', methods=['GET'])
def get_return_item():
    try:
        with db.connection.cursor() as cursor:
            # rentals.status 에서 '반납 완료'인 대여만, 그에 해당하는 items 정보를 가져옵니다
            cursor.execute("""
                SELECT 
                    i.item_id, i.name, i.price, i.quantity, i.created_at,
                    r.status, r.return_date, r.item_condition
                FROM rentals r
                JOIN items i ON r.item_id = i.item_id
                WHERE r.status = '반납 완료'
            """)
            items = cursor.fetchall()
        return render_template('return_item.html', items=items)
    except Exception as e:
        return str(e), 500

#반납 목록 엑셀 다운로드 (상단 import 확인 필)
#pip install pands openpyxl 필요

@app.route('/download_returns')
def download_returns():
    try:
        query = """
        SELECT i.item_id, i.name, i.price, i.quantity, i.created_at, r.item_condition,
               u.name AS user_name, r.return_date
        FROM rentals r
        JOIN items i ON r.item_id = i.item_id
        JOIN users u ON r.user_id = u.user_id
        WHERE r.status = '반납완료'
        """
        
        with db.connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        # 컬럼명 정의
        df = pd.DataFrame(results, columns=[
            '물품ID', '물품명', '가격', '수량', '등록일시', '물품상태', '사용자명', '반납일시'
        ])

        # 메모리 버퍼에 저장
        output = io.BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name='반납리스트.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
