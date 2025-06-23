import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.applications import MobileNetV2 # <-- 전이 학습을 위해 MobileNetV2 임포트

import matplotlib.pyplot as plt
import numpy as np
import os
import random

# --- 1. 데이터셋 경로 설정 ---
# PlantVillage 데이터셋의 압축을 푼 최상위 폴더 경로를 여기에 입력하세요.
# 예: data_dir = '/content/drive/MyDrive/Colab_Notebooks/PlantVillage_Dataset' (Colab 사용 시)
data_dir = 'PlantVillage' # 사용자님의 기존 설정 유지

# 데이터셋 폴더 존재 여부 확인 (중요!)
if not os.path.exists(data_dir):
    print(f"오류: '{data_dir}' 경로를 찾을 수 없습니다.")
    print("PlantVillage 데이터셋의 압축을 풀고 올바른 경로를 설정해 주세요.")
    print("예상되는 폴더 구조: PlantVillage_Dataset/Apple___Black_rot/... 등")
    exit() # 경로가 없으면 스크립트 종료

VALIDATION_SPLIT = 0.2

# --- 2. 이미지 전처리 및 데이터 증강 (Data Augmentation) ---
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
    seed=42
)

validation_generator = train_datagen.flow_from_directory(
    data_dir,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation', # 검증 세트
    seed=42
)

num_classes = len(train_generator.class_indices)
class_names = list(train_generator.class_indices.keys())
print(f"\n감지된 클래스 수: {num_classes}")
print(f"클래스 매핑 (알파벳 순): {train_generator.class_indices}")
sorted_class_names = sorted(class_names, key=lambda x: train_generator.class_indices[x])
print(f"정렬된 클래스 이름: {sorted_class_names}\n")
print("✅ 전이 학습 모델 (MobileNetV2) 구축 시작...")
base_model = MobileNetV2(input_shape=(IMG_HEIGHT, IMG_WIDTH, 3),
                         include_top=False,
                         weights='imagenet')

# 기본 모델의 가중치를 고정 (초기 학습 단계에서는 사전 학습된 특징 추출기를 그대로 사용)
base_model.trainable = False

# 새로운 분류 헤드(Classification Head)를 추가하여 우리의 데이터셋에 맞게 모델을 구성합니다.
model = Sequential([
    base_model, # 사전 학습된 MobileNetV2 모델의 특징 추출기 부분
    GlobalAveragePooling2D(), # 특징 맵을 1D 벡터로 평탄화 (Flatten보다 효율적)
    Dense(512, activation='relu'), # 새로운 완전 연결 레이어
    Dropout(0.5), # 과적합 방지
    Dense(num_classes, activation='softmax') # 최종 출력 레이어 (클래스 개수만큼)
])

# --- 5. 모델 컴파일 ---
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

# --- 6. 모델 학습 ---
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
model_checkpoint = ModelCheckpoint('best_plant_disease_model_transfer.h5', monitor='val_accuracy', save_best_only=True, mode='max', verbose=1)

EPOCHS = 50

print(f"\n모델 학습 시작 (총 {EPOCHS} 에포크, 조기 종료 활성화, MobileNetV2 특징 추출기 고정)...")
history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=validation_generator,
    callbacks=[early_stopping, model_checkpoint]
)

print("\n모델 학습 완료.")
print("\n학습 결과 시각화 중...")
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(len(acc))

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
# ModelCheckpoint가 이미 최적의 모델을 저장하지만, 최종 모델을 명시적으로 저장할 수도 있습니다.
model.save('final_plant_disease_model_transfer.h5')
print("최종 모델이 'final_plant_disease_model_transfer.h5'로 저장되었습니다.")
print("최고 성능 모델은 'best_plant_disease_model_transfer.h5'로 저장되었습니다.")

# --- 9. 새 이미지로 예측 (예시) ---
# 저장된 모델을 로드하여 새로운 이미지에 대해 예측을 수행합니다.
print("\n--- 새 이미지로 질병 예측 테스트 ---")

try:
    loaded_model = load_model('best_plant_disease_model_transfer.h5')
    print("최적의 저장된 전이 학습 모델 'best_plant_disease_model_transfer.h5' 로드 성공.")
except Exception as e:
    print(f"최적의 모델 로드 실패: {e}. 최종 모델을 로드합니다.")
    loaded_model = load_model('final_plant_disease_model_transfer.h5')

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
    score = predictions[0]

    predicted_class_index = np.argmax(score)
    confidence = 100 * np.max(score)

    predicted_class_name = sorted_class_names[predicted_class_index]

    print(f"이 이미지는 '{predicted_class_name}' (으)로 예측됩니다.")
    print(f"확신도: {confidence:.2f}%")

    plt.figure(figsize=(6, 6))
    plt.imshow(img)
    plt.title(f"예측: {predicted_class_name}\n확신도: {confidence:.2f}%")
    plt.axis('off')
    plt.show()

print("\n학습 데이터셋에서 랜덤 이미지 하나를 선택하여 예측 테스트합니다.")
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