import sys
import os
import json
import base64
from PIL import Image
from ultralytics import YOLO

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

root_dir = sys.argv[1] if len(sys.argv) > 1 else "../downloader/download_by_area/data/"

model = YOLO('../ultimo.pt')
class_names = model.names
skip_classes = {}

for dirpath, _, filenames in os.walk(root_dir):
    for f in filenames:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(dirpath, f)
            results = model.predict(source=image_path, save=False, conf=0.7)
            r = results[0]

            shapes = []
            for box in r.boxes:
                cls_id = int(box.cls[0])
                name = class_names[cls_id]
                if name in skip_classes:
                    continue
                xc, yc, bw, bh = box.xywh[0].tolist()
                x1, y1, x2, y2 = xc - bw/2, yc - bh/2, xc + bw/2, yc + bh/2

                shapes.append({
                    "label": name,
                    "points": [[x1, y1], [x2, y2]],
                    "group_id": None,
                    "description": "",
                    "shape_type": "rectangle",
                    "flags": {}
                })

            if shapes:
                img = Image.open(image_path)
                w, h = img.size
                image_data = image_to_base64(image_path)
                labelme_data = {
                    "version": "5.2.1",
                    "flags": {},
                    "shapes": shapes,
                    "imagePath": os.path.basename(image_path),
                    "imageData": image_data,
                    "imageHeight": h,
                    "imageWidth": w
                }
                json_path = os.path.splitext(image_path)[0] + ".json"
                if os.path.exists(json_path):
                    print(f"Skipping {image_path} (already labeled)")
                    continue

                with open(json_path, 'w') as f:
                    json.dump(labelme_data, f, indent=4)

print("Ready! Images have been labeled")
