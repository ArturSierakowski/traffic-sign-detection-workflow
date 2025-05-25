import os
import json
import glob
from pathlib import Path

category_to_id = {
    "A-1": 0, "A-2": 1, "A-3": 2, "A-4": 3, "A-5": 4, "A-6": 5, "A-7": 6, "A-8": 7, "A-9": 8, "A-11": 9,
    "A-12": 10, "A-14": 11, "A-15": 12, "A-16": 13, "A-17": 14, "A-18": 15, "A-20": 16, "A-21": 17,
    "A-24": 18, "A-29": 19, "A-30": 20, "A-32": 21, "B-1": 22, "B-2": 23, "B-5": 24, "B-9": 25,
    "B-15/16": 26, "B-18/19": 27, "B-20": 28, "B-21": 29, "B-22": 30, "B-23": 31, "B-25/26": 32,
    "B-27/28": 33, "B-32": 34, "B-33": 35, "B-34": 36, "B-35": 37, "B-36": 38, "B-41": 39, "B-42": 40,
    "B-43": 41, "B-44": 42, "C-2": 43, "C-4": 44, "C-5": 45, "C-6": 46, "C-9": 47, "C-10": 48,
    "C-11": 49, "C-12": 50, "C-13": 51, "C-13/16": 52, "C-16": 53, "D-1": 54, "D-2": 55, "D-3": 56,
    "D-4a": 57, "D-4b": 58, "D-5": 59, "D-6": 60, "D-7": 61, "D-8": 62, "D-9": 63, "D-10": 64,
    "D-11/12": 65, "D-14": 66, "D-15/16/17": 67, "D-18": 68, "D-23": 69, "D-23a": 70, "D-26": 71,
    "D-26b": 72, "D-26c": 73, "D-27": 74, "D-28": 75, "D-29": 76, "D-31": 77, "D-40": 78, "D-42": 79,
    "D-43": 80, "D-44": 81, "D-45": 82, "D-47": 83, "D-49": 84, "D-50": 85, "D-52": 86, "F-5/6": 87,
    "F-7": 88, "F-9": 89, "F-10": 90, "F-11": 91, "F-14": 92, "F-21/22": 93, "G-1": 94, "G-2": 95,
    "G-3/4": 96, "P-8a": 97, "P-8b": 98, "P-8d": 99, "P-8e": 100, "P-8f": 101, "P-8i": 102,
    "P-9a": 103, "P-9b": 104
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
