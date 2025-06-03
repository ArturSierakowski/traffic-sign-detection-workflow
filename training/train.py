from ultralytics import YOLO
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
            "patience": 10,
            "device": "cuda",
            "augment": False,
            "project": "runs/detect",
            "name": "exp_yolo_mlflow",
            "exist_ok": False
        }

        model = YOLO("yolo11n.pt")
        results = model.train(**params)
