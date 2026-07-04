import os
import time
import torch
import torch.nn as nn
import torchvision.transforms.v2 as transforms
from PIL import Image
from torchvision.models import resnet50

# ==========================================
# 1. 설정 (경로 자동 계산)
# ==========================================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "baby_resnet50_all_layers.pth")

CLASS_NAMES = ["눕다","터미타임","뒤집다","앉다","기다","서다","걷다","오르다","손동작","놀이","독서","상호작용","식사","위생","수면"]

# ==========================================
# 2. 이미지 전처리 정의
# ==========================================
test_transforms = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToImage(),
    transforms.ToDtype(torch.float32, scale=True),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# ==========================================
# 3. 모델 빌드 및 가중치 불러오기
# ==========================================
def load_inference_model():
    model = resnet50(weights=None)
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(num_features, len(CLASS_NAMES))
    )
    
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
        model = model.to(DEVICE)
        model.eval()
        print(f"모델 가중치 로드 완료: {MODEL_PATH}")
        return model
    else:
        raise FileNotFoundError(f"가중치 파일을 찾을 수 없습니다: {MODEL_PATH}")

# ==========================================
# 4. 실제 이미지 예측 및 시간 계산 함수
# ==========================================
def predict_image(model, img_path):
    if not os.path.exists(img_path):
        print(f"이미지를 찾을 수 없습니다: {img_path}")
        return
        
    start_time = time.time()
    
    image = Image.open(img_path).convert("RGB")
    input_tensor = test_transforms(image).unsqueeze(0).to(DEVICE)
    
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted_idx = torch.max(probabilities, dim=1)
        
    # 시간 측정 종료 및 차이 계산
    end_time = time.time()
    elapsed_time = end_time - start_time
        
    predicted_class = CLASS_NAMES[predicted_idx.item()]
    print("-" * 40)
    print(f"입력 이미지: {os.path.basename(img_path)}")
    print(f"예측 결과: {predicted_class}")
    print(f"확신도: {confidence.item() * 100:.2f}%")
    print(f"소요 시간: {elapsed_time:.4f}초")
    print("-" * 40)

    return predicted_class

# ==========================================
# 5. 실행
# ==========================================
if __name__ == "__main__":
    try:
        net = load_inference_model()
    except Exception as e:
        print(e)
        exit()

    TARGET_IMAGE_PATH = os.path.join(CURRENT_DIR, "test_baby_image.jpg") 
    
    predict_image(net, TARGET_IMAGE_PATH)
