import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt
import numpy as np
import os
import random # 예측 예시를 위해 추가

data_dir = 'PlantVillage'

# 데이터셋 폴더 존재 여부 확인 (중요!)
if not os.path.exists(data_dir):
    print(f"오류: '{data_dir}' 경로를 찾을 수 없습니다.")
    exit() # 경로가 없으면 스크립트 종료

VALIDATION_SPLIT = 0.2 



train_datagen = ImageDataGenerator(
    rescale=1./255,             # 픽셀 값을 0-1 사이로 정규화 (필수)
    rotation_range=20,          # 20도 내에서 랜덤하게 회전
    width_shift_range=0.1,      # 10% 내에서 좌우 이동
    height_shift_range=0.1,     # 10% 내에서 상하 이동
    shear_range=0.1,            # 전단 변환
    zoom_range=0.1,             # 10% 내에서 확대/축소
    horizontal_flip=True,       # 좌우 반전
    fill_mode='nearest',        # 새로 생성되는 픽셀을 채우는 방식
    validation_split=VALIDATION_SPLIT # 여기에서 학습/검증 데이터 분할을 설정
)

IMG_HEIGHT = 150 # 이미지 높이
IMG_WIDTH = 150  # 이미지 너비
BATCH_SIZE = 32  # 배치 크기

print(f"\n데이터 로딩 중... 경로: {data_dir}")

train_generator = train_datagen.flow_from_directory(
    data_dir,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training', # 학습 세트
    seed=42 # 재현성을 위한 시드 설정
)

validation_generator = train_datagen.flow_from_directory(
    data_dir,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation', # 검증 세트
    seed=42 # 재현성을 위한 시드 설정
)

# 감지된 클래스 개수 및 매핑 확인
num_classes = len(train_generator.class_indices)
class_names = list(train_generator.class_indices.keys())
print(f"\n감지된 클래스 수: {num_classes}")
print(f"클래스 매핑 (알파벳 순): {train_generator.class_indices}")
# 클래스 이름 순서 (예측 시 필요)
sorted_class_names = sorted(class_names, key=lambda x: train_generator.class_indices[x])
print(f"정렬된 클래스 이름: {sorted_class_names}\n")

# --- 4. CNN 모델 구축 ---
# 이미지 분류에 효과적인 합성곱 신경망 (Convolutional Neural Network) 모델을 정의합니다.

model = Sequential([
    # 첫 번째 Conv2D 레이어: 32개의 필터, 3x3 커널, 활성화 함수 relu, 입력 이미지 형태 지정
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
    MaxPooling2D((2, 2)), # 2x2 풀링 (이미지 크기를 절반으로 줄임)

    # 두 번째 Conv2D 레이어: 64개의 필터
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),

    # 세 번째 Conv2D 레이어: 128개의 필터
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),

    # 네 번째 Conv2D 레이어: 256개의 필터 (더 깊은 특징 추출)
    Conv2D(256, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),

    Flatten(), # 2D 특징 맵을 1D 벡터로 평탄화하여 Dense 레이어에 전달
    Dropout(0.5), # 50%의 뉴런을 랜덤하게 비활성화하여 과적합 방지

    Dense(512, activation='relu'), # 512개의 뉴런을 가진 완전 연결 레이어
    Dropout(0.3), # 30%의 뉴런을 랜덤하게 비활성화

    # 최종 출력 레이어: 클래스 개수만큼의 뉴런, Softmax 활성화 함수 (각 클래스에 대한 확률 출력)
    Dense(num_classes, activation='softmax')
])

# --- 5. 모델 컴파일 ---
# 모델 학습을 위한 설정: 최적화기, 손실 함수, 평가 지표
model.compile(optimizer='adam', # Adam 옵티마이저 (일반적으로 좋은 성능)
              loss='categorical_crossentropy', # 다중 클래스 분류를 위한 손실 함수
              metrics=['accuracy']) # 모델 성능 평가 지표: 정확도

model.summary() # 모델의 구조와 파라미터 개수 요약 출력

# --- 6. 모델 학습 ---
# 콜백 함수 설정 (학습 효율성 증가)
# EarlyStopping: 검증 손실이 더 이상 개선되지 않으면 학습 조기 종료
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
# ModelCheckpoint: 검증 정확도가 가장 좋은 모델을 저장
model_checkpoint = ModelCheckpoint('best_plant_disease_model.h5', monitor='val_accuracy', save_best_only=True, mode='max', verbose=1)


EPOCHS = 50 # 에포크 수 (전체 데이터셋을 반복하여 학습하는 횟수)
            # 처음에는 50 정도로 시작하고, EarlyStopping이 자동으로 최적 지점에서 멈춥니다.

print(f"\n모델 학습 시작 (총 {EPOCHS} 에포크, 조기 종료 활성화)...")
history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=validation_generator,
    callbacks=[early_stopping, model_checkpoint] # 콜백 적용
)

print("\n모델 학습 완료.")

# --- 7. 학습 결과 시각화 ---
print("\n학습 결과 시각화 중...")
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(len(acc)) # 실제 학습된 에포크 수

plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='훈련 정확도')
plt.plot(epochs_range, val_acc, label='검증 정확도')
plt.legend(loc='lower right')
plt.title('훈련 및 검증 정확도')
plt.xlabel('에포크')
plt.ylabel('정확도')
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='훈련 손실')
plt.plot(epochs_range, val_loss, label='검증 손실')
plt.legend(loc='upper right')
plt.title('훈련 및 검증 손실')
plt.xlabel('에포크')
plt.ylabel('손실')
plt.grid(True)

plt.tight_layout()
plt.show()

# --- 8. 모델 저장 ---
# ModelCheckpoint가 이미 최적의 모델을 저장했지만, 명시적으로 최종 모델을 저장할 수도 있습니다.
model.save('final_plant_disease_model.h5')
print("최종 모델이 'final_plant_disease_model.h5'로 저장되었습니다.")
print("최고 성능 모델은 'best_plant_disease_model.h5'로 저장되었습니다.")

# --- 9. 새 이미지로 예측 (예시) ---
# 저장된 모델을 로드하여 새로운 이미지에 대해 예측을 수행합니다.
print("\n--- 새 이미지로 질병 예측 테스트 ---")

# 최적의 모델 로드
try:
    loaded_model = load_model('best_plant_disease_model.h5')
    print("최적의 저장된 모델 'best_plant_disease_model.h5' 로드 성공.")
except Exception as e:
    print(f"최적의 모델 로드 실패: {e}. 최종 모델을 로드합니다.")
    loaded_model = load_model('final_plant_disease_model.h5')

def predict_disease(image_path, model, target_size=(IMG_HEIGHT, IMG_WIDTH)):
    if not os.path.exists(image_path):
        print(f"오류: 예측할 이미지 경로 '{image_path}'를 찾을 수 없습니다.")
        return

    print(f"'{image_path}' 이미지 예측 중...")
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=target_size)
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) # 배치 차원 (샘플 개수) 추가
    img_array = img_array / 255.0 # 정규화 (학습 시와 동일하게)

    predictions = model.predict(img_array)
    score = predictions[0] # predictions는 배치 차원을 포함하므로 첫 번째 샘플의 예측값을 가져옴

    # 소프트맥스 활성화 함수를 썼으므로 이미 확률 값입니다.
    predicted_class_index = np.argmax(score)
    confidence = 100 * np.max(score)

    predicted_class_name = sorted_class_names[predicted_class_index] # 미리 정렬된 클래스 이름 사용

    print(f"이 이미지는 '{predicted_class_name}' (으)로 예측됩니다.")
    print(f"확신도: {confidence:.2f}%")

    plt.figure(figsize=(6, 6))
    plt.imshow(img)
    plt.title(f"예측: {predicted_class_name}\n확신도: {confidence:.2f}%")
    plt.axis('off')
    plt.show()

# --- 실제 예측할 이미지 선택 및 실행 (예시) ---
# 학습 데이터셋의 특정 클래스에서 랜덤으로 이미지 하나를 선택하여 예측 테스트
# 이 부분은 예시이므로, 실제 진단하고 싶은 새로운 이미지가 있다면 해당 경로로 변경해주세요.

print("\n학습 데이터셋에서 랜덤 이미지 하나를 선택하여 예측 테스트합니다.")
# 데이터셋 내의 모든 클래스 폴더 경로 가져오기
all_class_paths = [os.path.join(data_dir, class_name) for class_name in sorted_class_names]
all_image_paths = []
for class_path in all_class_paths:
    if os.path.isdir(class_path):
        for img_name in os.listdir(class_path):
            if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                all_image_paths.append(os.path.join(class_path, img_name))

if all_image_paths:
    random_image_path = random.choice(all_image_paths)
    print(f"선택된 랜덤 이미지: {random_image_path}")
    predict_disease(random_image_path, loaded_model)
else:
    print("데이터셋에서 테스트할 이미지를 찾을 수 없습니다.")
    print("직접 예측할 이미지 경로를 'predict_disease()' 함수에 전달해 주세요.")