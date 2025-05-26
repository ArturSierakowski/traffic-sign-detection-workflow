# Traffic Sign Detection

This module contains scripts for downloading, processing, and training
a custom YOLO11 model for traffic sign detection using imagery from
Mapillary.\
It also supports experiment tracking with MLflow.

## 👤 Who is this for?

- Just want to use the app? You don't need this folder. The pretrained model is enough.

- Want to retrain the model or use custom data? Follow the steps below.

## 📦 Technologies Used
- Python 3.12
- PyTorch (CUDA 12.6)
- Labelme
- Albumentations
- Ultralytics YOLO11
- MLflow

> [!NOTE]
> This workflow was tested with Python 3.12 only

## 🗂️ Folder Structure
```
Model/
├── downloader/            # Mapillary data downloading
├── pipelines/             # Pipeline for preprocessing and dataset structuring
├── preprocessing/         # Additional transformation tools
├── training/              # Training scripts YOLO
├── utils/                 # Helper functions
└── requirements.txt       # Python dependencies
└── README.md              # You are reading it
```

## 🧪 Training Pipeline – Step by Step

1. Set up your environment
```bash
python -m venv .venv
.venv\Scripts\activate  # on Windows
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

2. Get a Mapillary token
- Visit [Mapillary Developers](https://www.mapillary.com/dashboard/developers)
- Register your application and allow "READ" access
- Copy your API token and place it in `downloader/.env`:
```
MAPILLARY_TOKEN=MLY|YOUR|TOKEN #set your token here
```

<details><summary>📸 Click to show Mapillary screenshots</summary>

<br>

![register application](.doc/snapshot_mapillary_register_application.jpg)
![token](.doc/snapshot_mapillary_token.jpg)

</details>


3. Add data sources

- Add coordinates to: `downloader/download_by_area/coordinates.txt`
- Add sequence IDs to: `downloader/download_by_area/sequences.txt`

4. Prepare the dataset 
```bash
python pipelines/prepare_data.py
```

5. Manually verify labels
Use [Labelme](https://github.com/wkentaro/labelme) to check/adjust bounding boxes.


6. Finalize the dataset
```bash
python pipelines/finalize_dataset.py
```

7. Augmentation
```bash
python preprocessing/split_aug_dataset.py
```

8. Train the model (You can enter your own parameters)
```bash
python training/train.py
```

> [!NOTE]  
> Training logs (metrics, artifacts) are saved to MLflow automatically if MLflow is installed and enabled in `train.py`.


9. Export the model (optional)
```bash
yolo export model=best.pt format=onnx
```

## 📂 Dataset and model training

<details>
    <summary>Click here to see </summary>

Mapillary is the site which you can download from and upload to cameos from a dash-camera.

This workflow allows you to download images either from the area (default = 0.005 geographical degrees)
or sequences (car routes).

### To download and label the images I created this pipeline:

[`prepare_data.py`](pipelines/prepare_data.py)

The pipeline leaves only labeled images and deletes the rest.\
It creates a new folder `dataset_prepared/` with all the images and labels in json format.

Your next step should be manually verifying the labels, because they are made by the pretrained model.

> [!IMPORTANT]
> How do you that?\
> Use [Labelme](https://github.com/wkentaro/labelme)

When everything is verified, you can go to the next step.

### To prepare the data in YOLO format use this pipeline:

[`finalize_dataset.py`](pipelines/finalize_dataset.py)

After running [`finalize_dataset.py`](pipelines/finalize_dataset.py),
the dataset is stored in a YOLO-compatible format and structure:

```
dataset/
├── images/
│   ├──1.jpg
│   ├──2.jpg
│   ├──3.jpg
│   ...
│
└── labels/
    ├──1.txt
    ├──2.txt
    ├──3.txt
    ...
```

### The last step before training your model is splitting it between sets (training, validation and test) and augmenting the training set

[`split_aug_dataset.py`](preprocessing/split_aug_dataset.py)

The dataset is automatically split into training, validation and training sets (70/20/10 split by default).
You can adjust this ratio in the split script.

I intentionally disabled YOLO11's built-in augmentations (like flipLR and mosaic)
to maintain full controlandconsistency of the training data.

Instead, augmentations are applied explicitly using Albumentations in the split_aug_dataset.py script.

This approach improves reproducibility and allows us to preview the dataset after augmentation and before training.
Each transformation is deterministic and configurable, which makes experiments more predictable.

Example augmentation setup:

```python
from albumentations import Compose, RandomBrightnessContrast, HueSaturationValue, RandomGamma, CLAHE

transform = Compose([
    RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.1, p=0.8),
    RandomGamma(p=0.5, gamma_limit=(80, 120)),
    HueSaturationValue(hue_shift_limit=2, sat_shift_limit=5, val_shift_limit=8, p=0.2),
    CLAHE(clip_limit=2.0, tile_grid_size=(8, 8), p=0.1),
])
```

The structure after running [`split_aug_dataset.py`](./preprocessing/split_aug_dataset.py)

```
dataset/
├── images/
├── labels/
├── train/
│   ├── images/
│   └── labels/
├── val/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

> [!TIP]
> When I don't like the augmentation, or I extend the dataset with new labeled images
> I delete only the train, val and test folders. 

### Training using the YOLO11 model

[`train.py`](training/train.py)

</details>

## 📊 Final results
| Metric       | Value |
|--------------|-------|
| mAP@0.5      | 0.85  |
| mAP@0.5:0.95 | 0.71  |
| Precision    | 0.81  |
| Recall       | 0.80  |

---

Author: [Artur Sierakowski](https://github.com/ArturSierakowski)\
Source repository: [traffic-sign-detection-workflow](https://github.com/ArturSierakowski/traffic-sign-detection-workflow)
