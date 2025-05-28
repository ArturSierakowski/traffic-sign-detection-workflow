import os
import json
import yaml
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# Paths
json_dir = "../dataset_prepared"
yaml_path = "../training/data.yaml"

# Load valid labels from data.yaml
with open(yaml_path, "r") as f:
    data_yaml = yaml.safe_load(f)
valid_labels = list(data_yaml.get("names", {}).values())

# Count labels in JSON files
label_counts = Counter()
for root, _, files in os.walk(json_dir):
    for filename in files:
        if filename.endswith(".json"):
            with open(os.path.join(root, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                for shape in data.get("shapes", []):
                    label = shape.get("label", "").strip()
                    if label in valid_labels:
                        label_counts[label] += 1

# Sort counts descending
sorted_counts = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)

# Split into top and remaining
top_n = 40
top = sorted_counts[:top_n]
rest = sorted_counts[top_n:]

# Seaborn color palettes
palette_top = sns.color_palette("crest", len(top))
palette_rest = sns.color_palette("crest", len(rest))

# Create two subplots
fig, axs = plt.subplots(2, 1, figsize=(22, 14), sharex=False)

# --- Plot 1: Top 22 ---
labels_top, counts_top = zip(*top)
axs[0].bar(labels_top, counts_top, color=palette_top)
axs[0].set_title("Top 40 most frequent classes")
axs[0].grid(axis='y', linestyle='--', alpha=0.5)
axs[0].tick_params(axis='x', rotation=90)

# Add value labels
for i, count in enumerate(counts_top):
    axs[0].text(i, count + 10, str(count), ha='center', va='bottom', fontsize=9)

# --- Plot 2: Remaining classes ---
labels_rest, counts_rest = zip(*rest)
axs[1].bar(labels_rest, counts_rest, color=palette_rest)
axs[1].set_title(f"Remaining {len(rest)} classes")
axs[1].grid(axis='y', linestyle='--', alpha=0.5)
axs[1].tick_params(axis='x', rotation=90)

# Optional: show labels if counts are not too small
for i, count in enumerate(counts_rest):
    if count >= 30:
        axs[1].text(i, count + 5, str(count), ha='center', va='bottom', fontsize=7)

# Layout and save
plt.tight_layout()
plt.savefig("class_instances_split_top40.png")
plt.show()
