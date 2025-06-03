from ultralytics import YOLO
from pathlib import Path
import mlflow

if __name__ == "__main__":
    mlflow.set_tracking_uri("file:mlruns")
    mlflow.set_experiment("yolo-traffic-signs")

    with mlflow.start_run():
        params = {
            "cfg": "custom_args.yaml",
            "data": "data.yaml",
            "epochs": 100,
            "batch": 36,
            "imgsz": 640,
            "patience": 15,
            "device": "cuda",
            "augment": False,
            "project": "runs/detect",
            "name": "exp_yolo_mlflow",
            "exist_ok": False
        }

        model = YOLO("yolo11n.pt")
        results = model.train(**params)

        save_dir = Path(model.trainer.save_dir)
        try:
            mlflow.log_artifact(save_dir / "results.csv")
            mlflow.log_artifact(save_dir / "confusion_matrix.png")
            mlflow.log_artifact(save_dir / "weights" / "best.pt")
            mlflow.log_artifact(save_dir / "args.yaml")
        except Exception as e:
            print(f"[WARN] Couldn't log artifacts: {e}")
