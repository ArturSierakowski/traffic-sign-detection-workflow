import sys
import subprocess

print("Starting dataset preparation pipeline (Step 5/7)...")

seq_dir = "../downloader/download_by_sequence"
area_dir = "../downloader/download_by_area"
pre_dir = "../preprocessing"

print("Step 5: Moving labeled images to the dataset_prepared folder...")
subprocess.run([sys.executable, "move_labels_and_images.py", "../downloader/download_by_sequence/data"], cwd=pre_dir, check=True)
subprocess.run([sys.executable, "move_labels_and_images.py", "../downloader/download_by_area/data"], cwd=pre_dir, check=True)

print("Step 6: Copying labels to dataset/labels and converting JSON to YOLO TXT format...")
subprocess.run([sys.executable, "json_to_txt_conversion.py"], cwd=pre_dir, check=True)

print("Step 7: Copying images to dataset/images folder...")
subprocess.run([sys.executable, "copy_images.py"], cwd=pre_dir, check=True)

print("✅ Dataset preparation pipeline completed. Ready for training!")
