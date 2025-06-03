from ultralytics import YOLO
from pathlib import Path
import mlflow

if __name__ == "__main__":
    mlflow.set_tracking_uri("file:mlruns")
    mlflow.set_experiment("yolo-traffic-signs")

    with mlflow.start_run(run_name="resume-training", nested=True):
        model = YOLO("runs/detect/exp_yolo_mlflow/weights/last.pt")
        results = model.train(resume=True, name="exp_yolo_mlflow_resume")
