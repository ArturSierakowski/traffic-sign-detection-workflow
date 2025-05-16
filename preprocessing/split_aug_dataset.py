import os
import random
import cv2
import shutil
from albumentations import Compose, RandomBrightnessContrast, HueSaturationValue, RandomGamma, CLAHE

transform = Compose([
    RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.1, p=0.8),
    RandomGamma(p=0.5, gamma_limit=(80, 120)),
    HueSaturationValue(hue_shift_limit=2, sat_shift_limit=5, val_shift_limit=8, p=0.2),
    CLAHE(clip_limit=2.0, tile_grid_size=(8, 8), p=0.1),
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

os.makedirs(train_images_dir, exist_ok=True)
os.makedirs(train_labels_dir, exist_ok=True)
os.makedirs(val_images_dir, exist_ok=True)
os.makedirs(val_labels_dir, exist_ok=True)
os.makedirs(test_images_dir, exist_ok=True)
os.makedirs(test_labels_dir, exist_ok=True)

image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

random.shuffle(image_files)

train_size = int(len(image_files) * 0.7)
val_size = int(len(image_files) * 0.2)
test_size = len(image_files) - train_size - val_size

train_files = image_files[:train_size]
val_files = image_files[train_size:train_size + val_size]
test_files = image_files[train_size + val_size:]

def load_and_augment_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    augmented = transform(image=image)

    return augmented['image']

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

print(f'Sets have been split and augmented: {len(train_files)} train, {len(val_files)} val, {len(test_files)} test.')
