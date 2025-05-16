import os
from pathlib import Path

folder_with_images = "dataset/images"
folder_with_txts = "dataset/labels"

image_files = [f for f in Path(folder_with_images).glob('*') if f.is_file()]

for image_file in image_files:
    txt_file = Path(folder_with_txts) / (image_file.stem + ".txt")

    if not txt_file.exists():
        print(f"Deleting image: {image_file}")
        os.remove(image_file)

print("✅ Deleting finished!")
