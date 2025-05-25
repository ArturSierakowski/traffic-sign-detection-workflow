import mlflow
from ultralytics import YOLO
from pathlib import Path

# Logi trzymamy w training/mlruns
mlflow.set_tracking_uri("file:mlruns")
mlflow.set_experiment("yolo-traffic-signs")

if __name__ == "__main__":
    params = {
        "cfg": "custom_args.yaml",
        "data": "data.yaml",
        "epochs": 5,
        "batch": 8,
        "imgsz": 640,
        "device": "cuda",
        "augment": False,
        "project": "runs/detect",
        "name": "exp_yolo_mlflow",
        "exist_ok": False
    }

    with mlflow.start_run():
        for k, v in params.items():
            mlflow.log_param(k, v)

        model = YOLO("yolo11m.pt")
        results = model.train(**params)

        save_dir = Path(model.trainer.save_dir)

        try:
            mlflow.log_artifact(save_dir / "results.csv")
            mlflow.log_artifact(save_dir / "confusion_matrix.png")
            mlflow.log_artifact(save_dir / "weights" / "best.pt")
            mlflow.log_artifact(save_dir / "args.yaml")
        except Exception as e:
            print(f"[WARN] Nie udało się zalogować artefaktu: {e}")
