import os
import json
import glob
from pathlib import Path

category_to_id = {
    "A-1": 0, "A-2": 1, "A-3": 2, "A-4": 3, "A-5": 4, "A-6": 5, "A-7": 6, "A-8": 7, "A-9": 8, "A-10": 9,
    "A-11": 10, "A-12": 11, "A-13": 12, "A-14": 13, "A-15": 14, "A-16": 15, "A-17": 16, "A-18": 17, "A-19": 18,
    "A-20": 19, "A-21": 20, "A-22/23": 21, "A-24": 22, "A-29": 23, "A-30": 24, "A-31": 25, "A-32": 26, "B-1": 27,
    "B-2": 28, "B-3": 29, "B-4": 30, "B-5": 31, "B-7": 32, "B-9": 33, "B-10": 34, "B-11": 35, "B-13": 36,
    "B-13a": 37, "B-14": 38, "B-15/16": 39, "B-18/19": 40, "B-20": 41, "B-21": 42, "B-22": 43, "B-23": 44,
    "B-24": 45, "B-25/26": 46, "B-27/28": 47, "B-31": 48, "B-32": 49, "B-33": 50, "B-34": 51, "B-35": 52,
    "B-36": 53, "B-37": 54, "B-38": 55, "B-39": 56, "B-40": 57, "B-41": 58, "B-42": 59, "B-43": 60, "B-44": 61,
    "C-1": 62, "C-2": 63, "C-3": 64, "C-4": 65, "C-5": 66, "C-6": 67, "C-7": 68, "C-8": 69, "C-9": 70,
    "C-10": 71, "C-11": 72, "C-12": 73, "C-13": 74, "C-13a": 75, "C-13/16": 76, "C-14": 77, "C-15": 78,
    "C-16": 79, "C-16a": 80, "C-17": 81, "C-18": 82, "C-19": 83, "D-1": 84, "D-2": 85, "D-3": 86, "D-4a": 87,
    "D-4b": 88, "D-5": 89, "D-6": 90, "D-7": 91, "D-8": 92, "D-9": 93, "D-10": 94, "D-11/12": 95, "D-13": 96,
    "D-14": 97, "D-15/16/17": 98, "D-18": 99, "D-21": 100, "D-21a": 101,"D-22": 102, "D-23": 103, "D-23a": 104,
    "D-24": 105, "D-25": 106,"D-26": 107, "D-26a": 108, "D-26b": 109, "D-26c": 110, "D-26d": 111, "D-27": 112,
    "D-28": 113, "D-29": 114, "D-30": 115, "D-31": 116, "D-32": 117, "D-33": 118, "D-34": 119, "D-40": 120,
    "D-41": 121, "D-42": 122, "D-43": 123, "D-44": 124, "D-45": 125, "D-46": 126, "D-47": 127, "D-49": 128,
    "D-50": 129, "D-51": 130, "D-52": 131, "D-53": 132, "F-5/6": 133, "F-7": 134, "F-8": 135, "F-9": 136,
    "F-10": 137, "F-11": 138, "F-12": 139, "F-13": 140, "F-14": 141, "F-21/22": 142, "G-1": 143, "G-2": 144,
    "G-3/4": 145, "P-8a": 146, "P-8b": 147, "P-8c": 148, "P-8d": 149, "P-8e": 150, "P-8f": 151, "P-8i": 152,
    "P-9a": 153, "P-9b": 154
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
