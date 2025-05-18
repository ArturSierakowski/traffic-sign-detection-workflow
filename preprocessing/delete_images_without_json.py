import os
import shutil
import json
import sys

# Allow path as argument or use default
folder = sys.argv[1] if len(sys.argv) > 1 else "../downloader/download_by_sequence/data"

for dirpath, dirnames, filenames in os.walk(folder, topdown=False):
    for filename in filenames:
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            base = os.path.splitext(filename)[0]
            json_file = base + ".json"
            json_path = os.path.join(dirpath, json_file)

            if not os.path.exists(json_path):
                image_path = os.path.join(dirpath, filename)
                os.remove(image_path)
                print(f"Deleted: {image_path} (no JSON)")
            else:
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if not data.get("shapes"):
                            os.remove(json_path)
                            image_path = os.path.join(dirpath, filename)
                            os.remove(image_path)
                            print(f"Deleted: {image_path} and {json_path} (empty shapes)")
                except json.JSONDecodeError:
                    print(f"Invalid JSON: {json_path}")

# Remove empty subfolders (but not the root folder itself)
for dirpath, dirnames, filenames in os.walk(folder, topdown=False):
    if dirpath != folder and not os.listdir(dirpath):
        os.rmdir(dirpath)
        print(f"Deleted empty directory: {dirpath}")
