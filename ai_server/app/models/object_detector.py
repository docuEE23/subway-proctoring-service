# ai_server/app/models/object_detector.py
from typing import List, Dict
import numpy as np
from ultralytics import YOLO

# COCO 데이터셋에서 우리가 관심 있는 클래스들
# https://docs.ultralytics.com/datasets/coco/#dataset-yaml
TARGET_CLASSES = {
    67: 'cell phone', # 핸드폰
    73: 'laptop',     # 노트북 (전자패드/태블릿도 여기에 포함될 가능성이 높음)
    75: 'clock',      # 시계 (스마트워치를 이 항목으로 탐지)
    84: 'book'       # 책
}

class ObjectDetector:
    def __init__(self, model_name: str = 'yolov8n.pt'):
        """
        YOLOv8 모델을 사용하여 객체 탐지기를 초기화합니다.
        :param model_name: 사용할 YOLO 모델 파일명 (예: yolov8n.pt, yolov8s.pt 등)
        """
        self._model = None
        self.model_name = model_name

    def load(self) -> None:
        """
        필요한 경우 YOLOv8 모델을 메모리에 로드합니다.
        """
        if self._model is None:
            self._model = YOLO(self.model_name)

    def detect(self, img: np.ndarray, conf_threshold: float = 0.4) -> List[Dict[str, any]]:
        """
        이미지에서 전자기기, 책 등의 객체를 탐지합니다.
        :param img: 분석할 이미지 (OpenCV BGR 형식)
        :param conf_threshold: 탐지 신뢰도 임계값
        :return: 탐지된 객체 정보 리스트
        """
        self.load()
        
        # YOLO 모델에 이미지를 전달하여 객체 탐지 수행
        results = self._model(img, verbose=False)
        
        out: List[Dict[str, any]] = []
        # 결과에서 bounding box 정보 추출
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # 신뢰도가 임계값보다 낮은 객체는 무시
                conf = float(box.conf[0])
                if conf < conf_threshold:
                    continue

                # 클래스 ID 확인
                cls_id = int(box.cls[0])
                # 우리가 목표하는 클래스가 아니면 무시
                if cls_id not in TARGET_CLASSES:
                    continue
                
                # bounding box 좌표 추출 (x, y, 너비, 높이)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w, h = x2 - x1, y2 - y1
                
                out.append({
                    "x": x1,
                    "y": y1,
                    "w": w,
                    "h": h,
                    "score": conf,
                    "label": TARGET_CLASSES[cls_id]
                })
        return out
