import os
import cv2
import shutil
from sklearn.model_selection import train_test_split
from albumentations import (
    Compose, ShiftScaleRotate, RandomBrightnessContrast, RandomGamma,
    HueSaturationValue, GaussianBlur, MotionBlur, Perspective,
    OneOf, RandomRain, RandomFog, RandomShadow
)

transform = Compose([
    ShiftScaleRotate(shift_limit=0.05, scale_limit=0.2, rotate_limit=7, border_mode=0, p=0.4),
    Perspective(scale=(0.02, 0.05), p=0.3),
    OneOf([
        MotionBlur(blur_limit=3),
        GaussianBlur(blur_limit=(3, 5)),
    ], p=0.3),
    RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.4, p=0.5),
    RandomGamma(gamma_limit=(90, 110), p=0.3),
    HueSaturationValue(hue_shift_limit=5, sat_shift_limit=20, val_shift_limit=15, p=0.4),

    RandomRain(brightness_coefficient=0.95, drop_width=1, blur_value=2, p=0.2),
    RandomFog(fog_coef_lower=0.05, fog_coef_upper=0.1, alpha_coef=0.08, p=0.15),
    RandomShadow(shadow_roi=(0, 0.5, 1, 1), num_shadows_lower=1, num_shadows_upper=2, shadow_dimension=5, p=0.2)
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
test_ratio = 0.0

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
