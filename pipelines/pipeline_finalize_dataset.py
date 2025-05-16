import subprocess

print("Starting dataset preparation pipeline (Step 5/7)...")

# Step 5: Move valid images and labels to working folder
print("Step 5: Moving labeled images to the dataset folder...")
subprocess.run(["python", "../preprocessing/move_labels_and_images.py", "../downloader/download_by_sequence/data"])
subprocess.run(["python", "../preprocessing/move_labels_and_images.py", "../downloader/download_by_area/data"])

# Step 6: Convert JSON to YOLO TXT format
print("Step 6: Converting JSON labels to YOLO TXT format...")
subprocess.run(["python", "../preprocessing/json_to_txt_conversion.py"])

# Step 7: Copy images matching generated TXT files to dataset
print("Step 7: Copying images to dataset folder...")
subprocess.run(["python", "../preprocessing/copy_images_for_txt_labels.py"])

print("✅ Dataset preparation pipeline completed. Ready for training!")
