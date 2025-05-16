import os
from PIL import Image

# Ścieżki do folderów
labels_dir = "dataset/labels"
images_dir = "dataset/images"

# Próg powierzchni (w pikselach) – odpowiada 24x24
MIN_AREA_PX = 24 * 24

# Liczniki usuniętych
removed_images = 0
removed_labels = 0

for label_file in os.listdir(labels_dir):
    if not label_file.endswith(".txt"):
        continue

    label_path = os.path.join(labels_dir, label_file)
    image_name = os.path.splitext(label_file)[0]
    image_path = os.path.join(images_dir, image_name + ".jpg")

    if not os.path.exists(image_path):
        continue  # pomiń, jeśli obraz nie istnieje

    with Image.open(image_path) as img:
        width, height = img.size

    with open(label_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        _, x_center, y_center, w_rel, h_rel = map(float, parts)
        w_px = w_rel * width
        h_px = h_rel * height
        if w_px * h_px >= MIN_AREA_PX:
            new_lines.append(line)

    if new_lines:
        with open(label_path, "w") as f:
            f.writelines(new_lines)
    else:
        os.remove(label_path)
        removed_labels += 1
        if os.path.exists(image_path):
            os.remove(image_path)
            removed_images += 1

print(f"Usunięto {removed_labels} plików etykiet i {removed_images} odpowiadających im obrazów.")
