from ultralytics import YOLO
import pandas as pd

model = YOLO("training/runs/detect/exp_yolo_mlflow/weights/best.pt")

results = model.val(data="training/data.yaml", save=False)

cm = results.confusion_matrix

if cm is not None and hasattr(cm, 'matrix'):
    class_names = model.names

    df = pd.DataFrame(cm.matrix, index=class_names, columns=class_names)

    df.to_csv("confusion_matrix.csv")
    print("✅ Saved confusion_matrix.csv")
else:
    print("❌ Confusion matrix not found")
