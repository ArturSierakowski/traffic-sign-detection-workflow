import sys
import os
import shutil
import json

source_dir = sys.argv[1] if len(sys.argv) > 1 else "../downloader/download_by_sequence/data"
target_dir = sys.argv[2] if len(sys.argv) > 2 else "../dataset_prepared"

os.makedirs(target_dir, exist_ok=True)

for root, _, files in os.walk(source_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            base = os.path.splitext(file)[0]
            image_path = os.path.join(root, file)
            json_path = os.path.join(root, base + '.json')

            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    if data.get('shapes'):
                        target_image = os.path.join(target_dir, file)
                        target_json = os.path.join(target_dir, base + '.json')

                        if not os.path.exists(target_image):
                            shutil.move(image_path, target_image)
                            print(f"✅ Moved image: {file}")

                        if not os.path.exists(target_json):
                            shutil.move(json_path, target_json)
                            print(f"✅ Moved JSON: {base}.json")
                    else:
                        print(f"⛔ Empty shapes in: {base}.json — skipped")
                except json.JSONDecodeError:
                    print(f"❌ JSON error in: {base}.json — skipped")
            else:
                print(f"❌ Missing JSON for: {file} — skipped")

# Cleanup empty folders
for dirpath, dirnames, filenames in os.walk(source_dir, topdown=False):
    if not os.listdir(dirpath):
        os.rmdir(dirpath)
        print(f"🗑️ Removed empty folder: {dirpath}")
