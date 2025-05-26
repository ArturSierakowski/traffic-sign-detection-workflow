import sys
import os
import json
import base64
from PIL import Image
from ultralytics import YOLO

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def is_duplicate(shape1, shape2, tol=10):
    if shape1["label"] != shape2["label"]:
        return False
    p1a, p1b = shape1["points"]
    p2a, p2b = shape2["points"]
    return all(abs(a - b) <= tol for a, b in zip(p1a + p1b, p2a + p2b))

root_dir = sys.argv[1] if len(sys.argv) > 1 else "../downloader/download_by_area/data"

model = YOLO('../sigma.pt')
class_names = model.names
target_classes = {"A-7", "B-33", "B-36", "C-9", "D-1", "D-3", "D-6", "D-18", "D-15/16/17"}

for dirpath, _, filenames in os.walk(root_dir):
    for f in filenames:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(dirpath, f)
            json_path = os.path.splitext(image_path)[0] + ".json"

            if not os.path.exists(json_path):
                continue

            results = model.predict(source=image_path, save=False, conf=0.6)
            r = results[0]

            new_shapes = []
            for box in r.boxes:
                cls_id = int(box.cls[0])
                name = class_names[cls_id]
                if name not in target_classes:
                    continue
                xc, yc, bw, bh = box.xywh[0].tolist()
                x1, y1, x2, y2 = xc - bw/2, yc - bh/2, xc + bw/2, yc + bh/2

                new_shapes.append({
                    "label": name,
                    "points": [[x1, y1], [x2, y2]],
                    "group_id": None,
                    "description": "",
                    "shape_type": "rectangle",
                    "flags": {}
                })

            if new_shapes:
                img = Image.open(image_path)
                w, h = img.size
                image_data = image_to_base64(image_path)

                with open(json_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)

                existing_shapes = existing_data.get("shapes", [])
                combined_shapes = existing_shapes[:]

                for new_shape in new_shapes:
                    if not any(is_duplicate(new_shape, existing) for existing in existing_shapes):
                        combined_shapes.append(new_shape)

                labelme_data = {
                    "version": existing_data.get("version", "5.2.1"),
                    "flags": existing_data.get("flags", {}),
                    "shapes": combined_shapes,
                    "imagePath": os.path.basename(image_path),
                    "imageData": image_data,
                    "imageHeight": h,
                    "imageWidth": w
                }

                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(labelme_data, f, indent=4)
                print(f"Updated: {json_path}")

print("Ready! Selected classes have been added (no duplicates).")
