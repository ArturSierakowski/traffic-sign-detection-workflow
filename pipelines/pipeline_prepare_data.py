import sys
import subprocess

print("Starting data collection pipeline (Step 1/4)...")

seq_dir = "../downloader/download_by_sequence"
area_dir = "../downloader/download_by_area"
pre_dir = "../preprocessing"

print("Step 1: Downloading images by sequence...")
subprocess.run([sys.executable, "mapillary_download.py"], cwd=seq_dir, check=True)

print("Step 2: Downloading images by area...")
subprocess.run([sys.executable, "mapillary_download_area.py"], cwd=area_dir, check=True)

print("Step 3: Labeling images using the trained model...")
subprocess.run([sys.executable, "label_images_with_trained_model.py", "../downloader/download_by_sequence/data"], cwd=pre_dir, check=True)
subprocess.run([sys.executable, "label_images_with_trained_model.py", "../downloader/download_by_area/data"], cwd=pre_dir, check=True)

print("Step 4: Deleting images without corresponding JSON files...")
subprocess.run([sys.executable, "delete_images_without_json.py", "../downloader/download_by_sequence/data"], cwd=pre_dir, check=True)
subprocess.run([sys.executable, "delete_images_without_json.py", "../downloader/download_by_area/data"], cwd=pre_dir, check=True)

print("✅ Pipeline completed (Steps 1-4). Please review your labels before continuing.")
