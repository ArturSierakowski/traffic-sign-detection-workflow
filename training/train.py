from ultralytics import YOLO

if __name__ == "__main__":

    yaml_path = 'data.yaml'
    model = YOLO('yolo11m.pt')

    # model.load('runs/detect/train/weights/last.pt')

    model.train(
        cfg="custom_args.yaml",  # configure some augmentation
        data=yaml_path,
        epochs=2,
        batch=8,
        imgsz=640,
        device='cuda',
        augment=False,           # turn off built-in augmentation
    )
