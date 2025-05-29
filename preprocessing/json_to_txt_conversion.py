import os
import json
import glob
from pathlib import Path

category_to_id = {
    "A-1": 0, "A-2": 1, "A-3": 2, "A-4": 3, "A-5": 4, "A-6": 5, "A-7": 6, "A-8": 7, "A-9/10": 8,
    "A-11": 9, "A-12": 10, "A-14": 11, "A-15": 12, "A-16": 13, "A-17": 14, "A-18": 15, "A-20": 16,
    "A-21": 17, "A-24": 18, "A-29": 19, "A-30": 20, "A-32": 21, "B-1": 22, "B-2": 23, "B-5": 24,
    "B-9": 25, "B-15-19": 26, "B-20": 27, "B-21": 28, "B-22": 29, "B-23": 30, "B-25/26": 31,
    "B-32": 32, "B-33": 33, "B-42": 34, "B-36": 35, "B-41": 36, "B-43": 37, "B-44": 38, "C-2": 39,
    "C-4": 40, "C-5": 41, "C-6": 42, "C-9": 43, "C-10": 44, "C-11": 45, "C-12": 46, "C-13/16": 47,
    "D-1": 48, "D-2": 49, "D-3": 50, "D-4": 51, "D-6": 52, "D-7": 53, "D-8": 54, "D-9": 55,
    "D-10": 56, "D-11/12": 57, "D-14": 58, "D-15/16/17": 59, "D-18": 60, "D-23": 61,
    "D-23-29": 62, "D-40": 63, "D-42": 64, "D-43": 65, "D-45": 66, "D-46/52": 67,
    "D-50": 68, "F-5/6": 69, "F-7": 70, "F-10": 71, "F-11": 72, "F-14": 73, "DETOUR": 74,
    "G-1": 75, "G-2": 76, "G-3/4": 77, "P-8a": 78, "P-8b": 79, "P-8d": 80, "P-8e": 81,
    "P-8f": 82, "P-8i": 83, "P-9a": 84, "P-9b": 85
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

            MIN_AREA_PX = 32 * 32
            bbox_width_px = abs(x2 - x1)
            bbox_height_px = abs(y2 - y1)
            if bbox_width_px * bbox_height_px < MIN_AREA_PX:
                print(f"⚠️ Skipped small bounding box ({bbox_width_px}x{bbox_height_px}px) for class: {label}")
                continue

            print(f"🟩 {label}: YOLO format -> {class_id} {x_center} {y_center} {bbox_width} {bbox_height}")

            txt.write(f"{class_id} {x_center} {y_center} {bbox_width} {bbox_height}\n")

print("\n✅ Conversion finished!")
