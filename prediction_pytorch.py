import cv2
import threading
import time
from queue import Queue
from ultralytics import YOLO

VIDEO_PATH = "video.mp4"
MODEL_PATH = "ultimo_mini.pt"
FRAME_DELAY = 5
PREDICT_EVERY_N_FRAMES = 2

frame_buffer = Queue()
bbox_dict = {}
last_detections = []
model = YOLO(MODEL_PATH)


def predict_worker():
    while True:
        if not frame_buffer.empty():
            items = list(frame_buffer.queue)
            for frame_id, frame in items:
                if frame_id % PREDICT_EVERY_N_FRAMES == 0 and frame_id not in bbox_dict:
                    results = model(frame, imgsz=640, conf=0.8)[0]
                    detections = []
                    for box in results.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = float(box.conf)
                        cls = int(box.cls)
                        detections.append((x1, y1, x2, y2, conf, cls))
                    bbox_dict[frame_id] = detections
        time.sleep(0.01)


threading.Thread(target=predict_worker, daemon=True).start()

cap = cv2.VideoCapture(VIDEO_PATH)
frame_id = 0

cv2.namedWindow("Prediction", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Prediction", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_buffer.put((frame_id, frame.copy()))

    if frame_buffer.qsize() > FRAME_DELAY:
        display_id, display_frame = frame_buffer.get()

        if display_id in bbox_dict:
            last_detections = bbox_dict[display_id]
        detections = last_detections

        for x1, y1, x2, y2, conf, cls in detections:
            label = f"{model.names[cls]}"
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            text_x = x2 + 5 if x1 < frame.shape[1] // 2 else x1 - 50
            text_y = y1 + 15
            cv2.putText(display_frame, label, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Prediction", display_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    frame_id += 1

cap.release()
cv2.destroyAllWindows()
