import time
import cv2
import numpy as np


class RTSPError(Exception):
pass


def grab_frame(rtsp_url: str, timeout_sec: float = 5.0) -> np.ndarray:
cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
if not cap.isOpened():
cap.release(); raise RTSPError("Cannot open RTSP stream")
t0 = time.time(); frame = None
while time.time() - t0 < timeout_sec:
ok, f = cap.read()
if not ok:
time.sleep(0.02); continue
frame = f
if time.time() - t0 > 0.3: # 최신 프레임 확보
break
cap.release()
if frame is None:
raise RTSPError("Failed to grab frame from RTSP")
return frame
