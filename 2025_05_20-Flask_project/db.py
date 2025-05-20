# db.py 수정
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
                password='user1234',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print("MariaDB에 성공적으로 연결되었습니다.")
        except Error as e:
            print(f"MariaDB 연결 중 오류 발생: {e}")
            raise  # 연결 실패 시 예외를 발생시켜 명확히 알림

    def close(self):
        if self.connection:
            self.connection.close()
            print("MariaDB 연결이 종료되었습니다.")