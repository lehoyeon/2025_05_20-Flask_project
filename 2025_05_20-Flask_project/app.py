import os
from flask import Flask, render_template, request, redirect, url_for, flash
from rental_system import RentalSystem

# 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))
# 템플릿 폴더 경로
template_dir = os.path.join(current_dir, 'templates')

# 템플릿 폴더 존재 여부 확인 (디버깅용)
print(f"템플릿 폴더 경로: {template_dir}")
print(f"템플릿 폴더 존재 여부: {os.path.exists(template_dir)}")
if os.path.exists(template_dir):
    print(f"템플릿 폴더 내용: {os.listdir(template_dir)}")

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # 플래시 메시지를 사용하기 위해 필요합니다.

@app.route('/')
def index():
    system = RentalSystem()
    active_rentals = system.get_active_rentals()
    returned_rentals = system.get_returned_rentals()
    return render_template('index.html', rentals=active_rentals, returns=returned_rentals)


@app.route('/rent', methods=['POST'])
def rent():
    user_id = request.form.get('user_id')
    item_id = request.form.get('item_id')
    days = request.form.get('days')

    if not user_id or not item_id or not days:
        flash('모든 필드를 입력해주세요.')
        return redirect(url_for('index'))

    try:
        user_id = int(user_id)
        item_id = int(item_id)
        days = int(days)
    except ValueError:
        flash('입력값이 올바르지 않습니다.')
        return redirect(url_for('index'))

    system = RentalSystem()
    system.rent_item(user_id, item_id, days)
    flash('대여가 완료되었습니다.')
    return redirect(url_for('index'))

@app.route('/return', methods=['POST'])
def return_item():
    rental_id = request.form.get('rental_id')

    if not rental_id:
        flash('대여 ID를 입력해주세요.')
        return redirect(url_for('index'))

    try:
        rental_id = int(rental_id)
    except ValueError:
        flash('대여 ID가 올바르지 않습니다.')
        return redirect(url_for('index'))

    system = RentalSystem()
    system.return_item(rental_id)
    flash('반납이 완료되었습니다.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
