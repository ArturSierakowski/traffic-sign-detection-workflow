from ultralytics import YOLO
from pathlib import Path
import mlflow

if __name__ == "__main__":
    params = {
        "cfg": "custom_args.yaml",               # augmentations etc.
        "data": "data.yaml",
        "epochs": 70,
        "batch": 10,
        "imgsz": 640,
        "device": "cuda",
        "augment": False,
        "project": "runs/detect",
        "name": "exp_yolo_mlflow",
        "exist_ok": False,

        "mlflow": True,                          # YOLO automatically runs MLflow
        "experiment_name": "yolo-traffic-signs"
    }

    model = YOLO("yolo11m.pt")
    results = model.train(**params)

    save_dir = Path(model.trainer.save_dir)

    try:
        mlflow.log_artifact(save_dir / "results.csv")
        mlflow.log_artifact(save_dir / "confusion_matrix.png")
        mlflow.log_artifact(save_dir / "weights" / "best.pt")
        mlflow.log_artifact(save_dir / "args.yaml")
    except Exception as e:
        print(f"[WARN] Couldn't run the artefact {e}")
