import cv2
import torch
from cheating_detector import CheatingDetector
from face_recognizer import FaceRecognizer
from gaze_tracker import GazeTracker
from utils import display_results, CheatingStatus
import config

def main():
    """
    메인 함수: 웹캠 또는 RTSP 스트림을 통해 실시간으로 부정행위 탐지, 얼굴 인식, 시선 추적을 수행합니다.
    """
    # 디바이스 설정 (GPU 사용 가능하면 GPU 사용)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # AI 모델 클래스 인스턴스화
    try:
        # YOLOv10 모델을 사용하도록 CheatingDetector 업데이트
        cheating_detector = CheatingDetector(config.YOLO_MODEL_PATH, device, config.CONF_THRESHOLD)
        face_recognizer = FaceRecognizer(config.KNOWN_FACES_DIR)
        gaze_tracker = GazeTracker()
    except Exception as e:
        print(f"Error initializing models: {e}")
        return

    # 비디오 소스 선택 (config.RTSP_URL이 있으면 RTSP 스트림, 없으면 기본 웹캠)
    video_source = config.RTSP_URL if config.RTSP_URL else 0
    cap = cv2.VideoCapture(video_source)
    
    if not cap.isOpened():
        print(f"Error: Could not open video source: {video_source}")
        return
    print(f"Successfully opened video source: {video_source}")

    # 화면 창 설정
    cv2.namedWindow(config.WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(config.WINDOW_NAME, 1280, 720)

    # 상태 추적 변수
    cheating_status = CheatingStatus(
        persistence_threshold=config.OBJECT_PERSISTENCE_SECONDS,
        gaze_away_threshold=config.GAZE_AWAY_SECONDS
    )

    while True:
        # 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame. Stream might have ended.")
            break

        # 1. 부정행위 탐지 (YOLOv10)
        annotated_frame, detected_objects = cheating_detector.detect(frame)
        cheating_status.update_cheating_objects(detected_objects)

        # 2. 얼굴 인식 (성능 향상을 위해 프레임 축소 후 처리)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        face_locations, face_names = face_recognizer.recognize_faces(rgb_frame)
        cheating_status.update_face_recognition(face_names)
        
        # 원본 프레임 비율에 맞게 얼굴 위치 복원 후 그리기
        face_locations_orig = [(top*2, right*2, bottom*2, left*2) for (top, right, bottom, left) in face_locations]
        annotated_frame = face_recognizer.draw_face_boxes(annotated_frame, face_locations_orig, face_names)

        # 3. 시선 추적
        gray_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2GRAY)
        gaze_ratio_text, is_looking_away = gaze_tracker.track(gray_frame, annotated_frame)
        cheating_status.update_gaze(is_looking_away)

        # 4. 최종 결과 화면에 표시
        final_frame = display_results(
            annotated_frame,
            cheating_status,
            gaze_ratio_text
        )

        cv2.imshow(config.WINDOW_NAME, final_frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 자원 해제
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
