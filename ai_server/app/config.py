# --- 비디오 소스 설정 ---

# RTSP 스트림 URL을 입력하세요.
# 비워두거나 None으로 설정하면 기본 웹캠(0번)을 사용합니다.
# 예: "rtsp://username:password@ip_address:port/stream_path"
RTSP_URL = None 


# --- 모델 및 파일 경로 설정 ---

# 학습된 YOLOv10 모델 파일 경로
# 'yolov10n.pt'는 COCO 데이터셋으로 사전 학습된 모델입니다.
# 직접 학습한 커스텀 모델(.pt) 경로로 변경하여 사용하세요.
YOLO_MODEL_PATH = 'yolov10n.pt'

# 얼굴 인식을 위한 알려진 얼굴 이미지들이 저장된 디렉토리
# 이 디렉토리 안에 '이름.jpg', '이름.png' 형식으로 이미지를 저장하세요.
KNOWN_FACES_DIR = 'known_faces'

# dlib의 얼굴 랜드마크 예측 모델 파일 경로
# 이 파일은 dlib 웹사이트에서 다운로드해야 합니다.
# http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
DLIB_LANDMARK_PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"


# --- 탐지 및 경고 임계값 설정 ---

# YOLO 객체 탐지의 신뢰도 임계값 (0.0 ~ 1.0)
# 이 값보다 높은 신뢰도를 가진 객체만 탐지됩니다.
CONF_THRESHOLD = 0.4

# 특정 객체가 부정행위로 간주되기까지 지속적으로 탐지되어야 하는 시간 (초)
OBJECT_PERSISTENCE_SECONDS = 2.0

# 사용자가 화면을 보지 않는다고 판단하기까지의 시간 (초)
GAZE_AWAY_SECONDS = 3.0


# --- UI 설정 ---

# 결과 표시 창의 이름
WINDOW_NAME = 'AI Proctoring Service (YOLOv10)'
