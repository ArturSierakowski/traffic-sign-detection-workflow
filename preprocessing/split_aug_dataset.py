import os
import cv2
import shutil
from sklearn.model_selection import train_test_split
from albumentations import (
    Compose, RandomBrightnessContrast,
    GaussianBlur, MotionBlur, OneOf, GaussNoise,
    HueSaturationValue, RandomRain, RandomShadow
)

transform = Compose([
    OneOf([
        MotionBlur(blur_limit=5),
        GaussianBlur(blur_limit=(3, 5)),
    ], p=0.4),
    GaussNoise(std_range=(0.05, 0.1), p=0.2),

    OneOf([
        RandomRain(slant_range=(-20, 20), drop_length=30, drop_width=15, drop_color=(50, 50, 50), blur_value=30,
                   brightness_coefficient=0.7, rain_type="drizzle"),
        RandomShadow(shadow_roi=(0, 0.66, 1, 1), num_shadows_limit=(2, 3), shadow_dimension=5,
                     shadow_intensity_range=(0.3, 0.6))
    ], p=0.4),
    RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.5, p=0.5),
    HueSaturationValue(hue_shift_limit=10, sat_shift_limit=25, val_shift_limit=20, p=0.4),
])

dataset_dir = '../dataset'
images_dir = os.path.join(dataset_dir, 'images')
labels_dir = os.path.join(dataset_dir, 'labels')

train_images_dir = os.path.join(dataset_dir, 'train', 'images')
train_labels_dir = os.path.join(dataset_dir, 'train', 'labels')
val_images_dir = os.path.join(dataset_dir, 'val', 'images')
val_labels_dir = os.path.join(dataset_dir, 'val', 'labels')
test_images_dir = os.path.join(dataset_dir, 'test', 'images')
test_labels_dir = os.path.join(dataset_dir, 'test', 'labels')

for d in [train_images_dir, train_labels_dir, val_images_dir, val_labels_dir, test_images_dir, test_labels_dir]:
    os.makedirs(d, exist_ok=True)

image_files = []
image_labels = []

train_ratio = 0.8
val_ratio = 0.2
test_ratio = 0

assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Sum must give 1.0"

for fname in os.listdir(labels_dir):
    if fname.endswith('.txt'):
        label_path = os.path.join(labels_dir, fname)
        with open(label_path, 'r') as f:
            lines = f.readlines()
            if lines:
                first_class = int(lines[0].split()[0])
                img_file = fname.replace('.txt', '.jpg')
                if os.path.exists(os.path.join(images_dir, img_file)):
                    image_files.append(img_file)
                    image_labels.append(first_class)

# STRATIFIED SPLIT
if test_ratio > 0:
    X_temp, test_files, y_temp, y_test = train_test_split(
        image_files, image_labels, test_size=test_ratio, stratify=image_labels, random_state=42)

    val_ratio_rel = val_ratio / (train_ratio + val_ratio)
    train_files, val_files, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_ratio_rel, stratify=y_temp, random_state=42)

else:
    train_files, val_files, y_train, y_val = train_test_split(
        image_files, image_labels, test_size=val_ratio, stratify=image_labels, random_state=42)
    test_files = []


def move_and_augment_files(files, source_images, source_labels, target_images, target_labels, augment=False):
    for file in files:
        image_path = os.path.join(source_images, file)
        name, _ = os.path.splitext(file)
        label_path = os.path.join(source_labels, name + '.txt')

        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if augment:
            augmented = transform(image=image)
            image = augmented['image']

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(os.path.join(target_images, file), image)
        shutil.copy(label_path, os.path.join(target_labels, name + '.txt'))


move_and_augment_files(train_files, images_dir, labels_dir, train_images_dir, train_labels_dir, augment=True)
move_and_augment_files(val_files, images_dir, labels_dir, val_images_dir, val_labels_dir, augment=False)
move_and_augment_files(test_files, images_dir, labels_dir, test_images_dir, test_labels_dir, augment=False)

print(f'Sets have been split and augmented:\nTrain: {len(train_files)}\nVal: {len(val_files)}\nTest: {len(test_files)}')
