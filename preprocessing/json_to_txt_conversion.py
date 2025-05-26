import os
import json
import glob
from pathlib import Path

category_to_id = {
    "A-1": 0, "A-2": 1, "A-3": 2, "A-4": 3, "A-5": 4, "A-6": 5, "A-7": 6, "A-8": 7, "A-9": 8, "A-11": 9,
    "A-12": 10, "A-14": 11, "A-15": 12, "A-16": 13, "A-17": 14, "A-18": 15, "A-20": 16, "A-21": 17,
    "A-24": 18, "A-29": 19, "A-30": 20, "A-32": 21, "B-1": 22, "B-2": 23, "B-5": 24, "B-9": 25,
    "B-15/16": 26, "B-18/19": 27, "B-20": 28, "B-21": 29, "B-22": 30, "B-23": 31, "B-25/26": 32,
    "B-27/28": 33, "B-32": 34, "B-33": 35, "B-34": 36, "B-35": 37, "B-36": 38, "B-41": 39,
    "B-43": 40, "B-44": 41, "C-2": 42, "C-4": 43, "C-5": 44, "C-6": 45, "C-9": 46, "C-10": 47,
    "C-11": 48, "C-12": 49, "C-13/16": 50, "D-1": 51, "D-2": 52, "D-3": 53, "D-4a": 54, "D-4b": 55,
    "D-5": 56, "D-6": 57, "D-7": 58, "D-8": 59, "D-9": 60, "D-10": 61, "D-11/12": 62, "D-14": 63,
    "D-15/16/17": 64, "D-18": 65, "D-23": 66, "D-23a": 67, "D-26c": 68, "D-27": 69, "D-28": 70,
    "D-29": 71, "D-31": 72, "D-40": 73, "D-42": 74, "D-43": 75, "D-44": 76, "D-45": 77, "D-47": 78,
    "D-49": 79, "D-50": 80, "D-52": 81, "F-5/6": 82, "F-7": 83, "F-9": 84, "F-10": 85, "F-11": 86,
    "F-14": 87, "F-21/22": 88, "G-1": 89, "G-2": 90, "G-3/4": 91, "P-8a": 92, "P-8b": 93, "P-8d": 94,
    "P-8e": 95, "P-8f": 96, "P-8i": 97, "P-9a": 98, "P-9b": 99
}


input_folder = "../dataset_prepared"
output_folder = "../dataset/labels"

Path(output_folder).mkdir(parents=True, exist_ok=True)

json_files = glob.glob(f"{input_folder}/*.json")
print("🔍 Found JSONs:", json_files)

for file in json_files:
    if os.path.getsize(file) == 0:
        print(f"❌ Skipped empty JSON file: {file}")
        continue

    with open(file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON format in: {file}")
            continue

    print(f"\n📂 Processing file: {file}")
    print("📏 Image resolution:", data["imageWidth"], "x", data["imageHeight"])

    image_width = data["imageWidth"]
    image_height = data["imageHeight"]
    name = Path(file).stem

    output_file = Path(output_folder) / f"{name}.txt"

    with open(output_file, "w") as txt:
        for item in data["shapes"]:
            label = item["label"]
            if label not in category_to_id:
                print(f"⚠️ Skipped unknown class: {label}")
                continue

            class_id = category_to_id[label]
            points = item["points"]

            x1, y1 = points[0]
            x2, y2 = points[1]

            # Conversion to YOLO (normalized values 0-1)
            x_center = round(((x1 + x2) / 2) / image_width, 6)
            y_center = round(((y1 + y2) / 2) / image_height, 6)
            bbox_width = round(abs(x2 - x1) / image_width, 6)
            bbox_height = round(abs(y2 - y1) / image_height, 6)

            MIN_AREA_PX = 24 * 24
            bbox_width_px = abs(x2 - x1)
            bbox_height_px = abs(y2 - y1)
            if bbox_width_px * bbox_height_px < MIN_AREA_PX:
                print(f"⚠️ Skipped small bounding box ({bbox_width_px}x{bbox_height_px}px) for class: {label}")
                continue

            print(f"🟩 {label}: YOLO format -> {class_id} {x_center} {y_center} {bbox_width} {bbox_height}")

            txt.write(f"{class_id} {x_center} {y_center} {bbox_width} {bbox_height}\n")

print("\n✅ Conversion finished!")
