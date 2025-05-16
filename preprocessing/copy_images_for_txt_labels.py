import os
import shutil
from pathlib import Path

source_dir = "../prepared_dataset"
target_dir = "../dataset"

os.makedirs(target_dir, exist_ok=True)

txt_files = [Path(f).stem for f in os.listdir(target_dir) if f.endswith('.txt')]

for name in txt_files:
    for ext in ['.jpg', '.jpeg', '.png']:
        source_image_path = os.path.join(source_dir, name + ext)
        if os.path.exists(source_image_path):
            target_image_path = os.path.join(target_dir, name + ext)
            if not os.path.exists(target_image_path):
                shutil.copy(source_image_path, target_image_path)
                print(f"✅ Copied: {name + ext}")
            else:
                print(f"⚠️ Already exists: {name + ext}")
            break

print("✅ All required images have been copied.")
