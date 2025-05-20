# rental_system.py 수정
from db import Database
from datetime import datetime, timedelta

class RentalSystem:
    def __init__(self):
        self.db = Database()

    def rent_item(self, user_id, item_id, days):
        if not self.db.connection:
            print("데이터베이스에 연결할 수 없습니다.")
            return False

        try:
            with self.db.connection.cursor() as cursor:
                # 재고 확인
                cursor.execute("SELECT quantity, price FROM items WHERE item_id = %s", (item_id,))
                item = cursor.fetchone()
                if not item:
                    print("해당 물품이 존재하지 않습니다.")
                    return False
                if item['quantity'] <= 0:
                    print("해당 물품의 재고가 부족합니다.")
                    return False

                # 대여 정보 설정
                rent_date = datetime.now().date()
                due_date = rent_date + timedelta(days=days)
                price = item['price'] * days

                # 대여 내역 추가
                cursor.execute("""
                    INSERT INTO rentals (user_id, item_id, rent_date, due_date, status, price)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, item_id, rent_date, due_date, '대여중', price))

                # 재고 감소
                cursor.execute("UPDATE items SET quantity = quantity - 1 WHERE item_id = %s", (item_id,))

                self.db.connection.commit()
                print("대여가 완료되었습니다.")
                return True
        except Exception as e:
            print(f"대여 중 오류 발생: {e}")
            self.db.connection.rollback()
            return False
        finally:
            # 여기서 연결을 닫지 않음 - 다음 요청을 위해 유지
            pass

    def return_item(self, rental_id):
        if not self.db.connection:
            print("데이터베이스에 연결할 수 없습니다.")
            return False

        try:
            with self.db.connection.cursor() as cursor:
                # 대여 내역 확인
                cursor.execute("SELECT item_id, due_date FROM rentals WHERE rental_id = %s AND status = '대여중'", (rental_id,))
                rental = cursor.fetchone()
                if not rental:
                    print("유효한 대여 내역이 없습니다.")
                    return False

                item_id = rental['item_id']
                due_date = rental['due_date']
                return_date = datetime.now().date()

                # 상태 업데이트
                status = '반납 완료'
                if return_date > due_date:
                    status = '연체'

                cursor.execute("""
                    UPDATE rentals
                    SET return_date = %s, status = %s
                    WHERE rental_id = %s
                """, (return_date, status, rental_id))

                # 재고 증가
                cursor.execute("UPDATE items SET quantity = quantity + 1 WHERE item_id = %s", (item_id,))

                self.db.connection.commit()
                print("반납이 완료되었습니다.")
                return True
        except Exception as e:
            print(f"반납 중 오류 발생: {e}")
            self.db.connection.rollback()
            return False
        finally:
            # 여기서 연결을 닫지 않음 - 다음 요청을 위해 유지
            pass

    def __del__(self):
        # 객체가 소멸될 때 연결 닫기
        self.db.close()
        
    def get_active_rentals(self):
        """현재 대여 중인 내역 조회"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT rental_id, user_id, item_id, rent_date, due_date, price
                    FROM rentals
                    WHERE status = '대여중'
                """)
                return cursor.fetchall()
        except Exception as e:
            print(f"대여 중 내역 조회 오류: {e}")
            return []

    def get_returned_rentals(self):
        """반납 완료 내역 조회"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT rental_id, user_id, item_id, rent_date, return_date, status, price
                    FROM rentals
                    WHERE status = '반납 완료' OR status = '연체'
                """)
                return cursor.fetchall()
        except Exception as e:
            print(f"반납 완료 내역 조회 오류: {e}")
            return []
