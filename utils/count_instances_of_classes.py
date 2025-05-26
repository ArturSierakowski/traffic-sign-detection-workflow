import os
import json
from collections import Counter
import matplotlib.pyplot as plt

json_dir = "../dataset_prepared"

label_counts = Counter()

for root, _, files in os.walk(json_dir):
    for filename in files:
        if filename.endswith(".json"):
            with open(os.path.join(root, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                for shape in data.get("shapes", []):
                    label = shape.get("label")
                    if label:
                        label_counts[label] += 1

for label, count in label_counts.items():
    print(f"{label}: {count}")

plt.figure(figsize=(30, 10))
plt.bar(label_counts.keys(), label_counts.values())
plt.title("Sum of classes instances")
plt.xticks(rotation=90)
plt.yticks([0, 10, 20, 50, 100, 200, 500, 1000])
plt.tight_layout()

print("Number of labeled classes:", len(label_counts))

plt.savefig("class_instances.png")
plt.show()
