import subprocess

print("Starting data collection pipeline (Step 1/4)...")

# Step 1: Download by sequence
print("Step 1: Downloading images by sequence...")
subprocess.run(["python", "../downloader/download_by_sequence/mapillary_download.py"])

# Step 2: Download by area
print("Step 2: Downloading images by area...")
subprocess.run(["python", "../downloader/download_by_area/mapillary_download_area.py"])

# Step 3: Auto-label images with trained model
print("Step 3: Labeling images using the trained model...")
subprocess.run(["python", "../preprocessing/label_images_with_trained_model.py", "../downloader/download_by_sequence/data"])
subprocess.run(["python", "../preprocessing/label_images_with_trained_model.py", "../downloader/download_by_area/data"])

# Step 4: Delete images without JSON
print("Step 4: Deleting images without corresponding JSON files...")
subprocess.run(["python", "../preprocessing/delete_images_without_json.py", "../downloader/download_by_sequence/data"])
subprocess.run(["python", "../preprocessing/delete_images_without_json.py", "../downloader/download_by_area/data"])

print("✅ Pipeline completed (Steps 1-4). Please review your labels before continuing.")
