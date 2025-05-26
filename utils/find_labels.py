import os
import json

folder = "../dataset_prepared"
targeted_classes = {'A-5'}

matching_jsons = []

for file in os.listdir(folder):
    if file.endswith('.json'):
        path = os.path.join(folder, file)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for shape in data.get('shapes', []):
                    if shape.get('label') in targeted_classes:
                        matching_jsons.append(file)
                        break  # wystarczy jedno trafienie
        except Exception as e:
            print(f"❌ Error during processing {file}: {e}")

print("\n✅ JSONs containing " + ", ".join(sorted(targeted_classes)) + ":")
for name in matching_jsons:
    print(name)
