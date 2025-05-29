from ultralytics import YOLO
from pathlib import Path
import mlflow

if __name__ == "__main__":
    mlflow.set_tracking_uri("file:mlruns")
    mlflow.set_experiment("yolo-traffic-signs")

    with mlflow.start_run(run_name="resume-training", nested=True):
        model = YOLO("runs/detect/exp_yolo_mlflow2/weights/last.pt")
        results = model.train(resume=True, name="exp_yolo_mlflow2_resume")

        save_dir = Path(model.trainer.save_dir)
        try:
            files_to_log = [
                save_dir / "confusion_matrix.png",
                save_dir / "weights" / "best.pt",
                save_dir / "args.yaml",
                save_dir / "results.csv"
            ]
            for f in files_to_log:
                if f.exists():
                    mlflow.log_artifact(f)
        except Exception as e:
            print(f"[WARN] Couldn't log artifacts: {e}")
