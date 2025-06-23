import os
import io
import numpy as np
from PIL import Image

# Flask 웹 프레임워크 임포트
from flask import Flask, request, render_template_string, jsonify

# TensorFlow 및 Keras 임포트
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image # tensorflow.keras.utils.image 로 변경될 수 있음

# --- 1. 전역 설정 변수 ---
# 모델 파일 경로 (이 스크립트와 같은 폴더에 모델 파일이 있어야 합니다.)
MODEL_PATH = 'best_plant_disease_model.h5'

# 학습 시 사용했던 이미지 크기와 동일하게 설정 (이전 코드에서 150x150으로 설정했습니다.)
IMG_HEIGHT, IMG_WIDTH = 150, 150

# !!! 중요: 이 부분을 학습 시 출력된 '정렬된 클래스 이름'에 맞춰 정확히 입력해야 합니다. !!!
# 예시: ['Apple___Black_rot', 'Apple___healthy', 'Corn_(maize)___Common_rust', ...]
# 정확한 클래스 순서가 아니면 예측 결과가 잘못될 수 있습니다.
CLASS_NAMES = [
    'Apple___Black_rot', 'Apple___healthy', 'Apple___Cedar_apple_rust', 'Apple___scab',
    'Cherry___healthy', 'Cherry___Powdery_mildew',
    'Corn_(maize)___Common_rust', 'Corn_(maize)___healthy', 'Corn_(maize)___Northern_Leaf_Blight',
    'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___healthy', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
    'Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___healthy', 'Strawberry___Leaf_scorch',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___healthy', 'Tomato___Late_blight',
    'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot', 'Tomato___Tomato_mosaic_virus', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus'
] # PlantVillage 데이터셋의 일반적인 클래스 목록 예시

# --- 2. Flask 애플리케이션 초기화 ---
app = Flask(__name__)

# --- 3. 모델 로드 ---
# 서버 시작 시 모델을 한 번만 로드하여 효율성을 높입니다.
model = None
try:
    if os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
        print(f"✅ 모델 '{MODEL_PATH}' 로드 성공!")
    else:
        print(f"❌ 오류: 모델 파일 '{MODEL_PATH}'을(를) 찾을 수 없습니다. 이 스크립트와 같은 폴더에 모델 파일을 넣어주세요.")
except Exception as e:
    print(f"❌ 모델 로드 중 예외 발생: {e}")

# --- 4. 이미지 전처리 함수 ---
def preprocess_image(img_stream_or_path, target_size=(IMG_HEIGHT, IMG_WIDTH)):
    """
    이미지 스트림(업로드된 파일) 또는 파일 경로에서 이미지를 로드하고 전처리합니다.
    """
    if isinstance(img_stream_or_path, str): # 파일 경로인 경우
        img = image.load_img(img_stream_or_path, target_size=target_size)
    else: # 이미지 바이트 스트림인 경우 (request.files에서 읽은 파일)
        img = Image.open(io.BytesIO(img_stream_or_path.read()))
        img = img.resize(target_size) # PIL Image 객체를 resize

    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) # 배치 차원 추가 (모델 입력 형태: (1, height, width, 3))
    img_array /= 255.0 # 정규화 (0-1 스케일)
    return img_array

# --- 5. HTML 템플릿 정의 (파이썬 코드 내에 문자열로 포함) ---
# 이렇게 하면 별도의 .html 파일 없이 하나의 .py 파일로 실행 가능합니다.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>농작물 질병 진단 서비스</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f4f7f6; color: #333; display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
        .container { background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); padding: 30px; max-width: 650px; width: 90%; text-align: center; margin-bottom: 30px; }
        h1 { color: #2c3e50; margin-bottom: 25px; font-size: 2em; }
        .upload-section { margin-bottom: 30px; }
        input[type="file"] { border: 1px solid #ddd; padding: 10px; border-radius: 8px; width: calc(100% - 22px); margin-bottom: 15px; background-color: #fcfcfc; font-size: 1em; cursor: pointer; }
        button { background-color: #28a745; color: white; border: none; padding: 12px 25px; border-radius: 8px; font-size: 1.1em; cursor: pointer; transition: background-color 0.3s ease; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2); }
        button:hover { background-color: #218838; }
        #result-section { margin-top: 25px; padding: 20px; border-top: 1px solid #eee; text-align: left; }
        #result-section h2 { color: #0056b3; margin-bottom: 15px; font-size: 1.5em; }
        #result-section p { margin-bottom: 8px; font-size: 1.1em; line-height: 1.5; }
        #result-section strong { color: #d9534f; }
        #uploaded-image { max-width: 100%; height: auto; border-radius: 8px; margin-top: 20px; border: 1px solid #eee; }
        .error-message { color: red; font-weight: bold; margin-top: 10px; }
        footer { margin-top: auto; padding-top: 20px; color: #777; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 농작물 질병 진단 서비스 🌿</h1>
        <p>농작물 잎 이미지를 업로드하여 질병을 진단해 보세요.</p>

        <div class="upload-section">
            <form id="upload-form" enctype="multipart/form-data">
                <input type="file" name="file" id="file-input" accept="image/*" required>
                <button type="submit">진단하기</button>
            </form>
        </div>

        <div id="result-section">
            <h2>진단 결과</h2>
            <p id="status-message">이미지를 업로드하면 결과가 여기에 표시됩니다.</p>
            <p>예측된 질병: <strong id="predicted-class">N/A</strong></p>
            <p>확신도: <strong id="confidence">N/A</strong></p>
            <div style="text-align: center;">
                <img id="uploaded-image" src="#" alt="업로드된 이미지" style="display:none;">
            </div>
        </div>
    </div>
    <footer>
        <p>&copy; 2025 AI Plant Disease Diagnosis. All rights reserved.</p>
    </footer>

    <script>
        const uploadForm = document.getElementById('upload-form');
        const fileInput = document.getElementById('file-input');
        const statusMessage = document.getElementById('status-message');
        const predictedClassSpan = document.getElementById('predicted-class');
        const confidenceSpan = document.getElementById('confidence');
        const uploadedImage = document.getElementById('uploaded-image');

        uploadForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // 기본 폼 제출 방지

            const formData = new FormData(this);
            predictedClassSpan.textContent = '진단 중...';
            confidenceSpan.textContent = '진단 중...';
            statusMessage.textContent = '모델이 이미지를 분석하고 있습니다...';
            uploadedImage.style.display = 'none'; // 이전 이미지 숨기기

            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const reader = new FileReader();
                reader.onload = function(e) {
                    uploadedImage.src = e.target.result;
                    uploadedImage.style.display = 'block';
                };
                reader.readAsDataURL(file); // 이미지 미리보기
            }

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (data.error) {
                    statusMessage.innerHTML = `<p class="error-message">오류: ${data.error}</p>`;
                    predictedClassSpan.textContent = 'N/A';
                    confidenceSpan.textContent = 'N/A';
                } else {
                    statusMessage.textContent = '진단 완료!';
                    predictedClassSpan.textContent = data.predicted_class;
                    confidenceSpan.textContent = data.confidence;
                }
            } catch (error) {
                statusMessage.innerHTML = `<p class="error-message">네트워크 오류 또는 서버 응답 문제: ${error.message}</p>`;
                predictedClassSpan.textContent = 'N/A';
                confidenceSpan.textContent = 'N/A';
            }
        });
    </script>
</body>
</html>
"""

# --- 6. Flask 라우트 정의 ---
@app.route('/')
def index():
    """메인 페이지 (이미지 업로드 폼)를 렌더링합니다."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/predict', methods=['POST'])
def predict():
    """업로드된 이미지를 받아 질병을 예측하고 결과를 JSON으로 반환합니다."""
    if model is None:
        return jsonify({'error': '모델이 로드되지 않았습니다. 서버 로그를 확인해주세요.'}), 500

    if 'file' not in request.files:
        return jsonify({'error': '파일이 요청에 포함되지 않았습니다.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '선택된 파일이 없습니다.'}), 400

    if file:
        try:
            # 이미지 전처리
            processed_img = preprocess_image(file)

            # 예측 수행
            predictions = model.predict(processed_img)
            score = predictions[0] # 첫 번째 (유일한) 샘플의 예측 결과

            predicted_class_index = np.argmax(score)
            # 클래스 이름은 CLASS_NAMES 리스트에서 인덱스에 따라 가져옵니다.
            predicted_class_name = CLASS_NAMES[predicted_class_index]
            confidence = float(np.max(score) * 100) # 확신도 %

            return jsonify({
                'predicted_class': predicted_class_name,
                'confidence': f"{confidence:.2f}%"
            })

        except Exception as e:
            # 예측 또는 전처리 중 오류 발생 시
            return jsonify({'error': f'예측 중 오류 발생: {str(e)}'}), 500

# --- 7. 애플리케이션 실행 ---
if __name__ == '__main__':
    # Flask 개발 서버 실행
    # debug=True 는 개발 중 편리하지만, 실제 배포 시에는 False로 설정해야 합니다.
    app.run(debug=True, host='0.0.0.0', port=5000)
    # host='0.0.0.0'은 외부 접속을 허용합니다 (Colab, Docker 등에서 필요).