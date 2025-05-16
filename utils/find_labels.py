import os
import json

folder = r'C:\Users\artur\PycharmProjects\znaki_mapillary\dataset_nowy'
interesujace_klasy = {'A-5'}

pasujace_jsony = []

for file in os.listdir(folder):
    if file.endswith('.json'):
        path = os.path.join(folder, file)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for shape in data.get('shapes', []):
                    if shape.get('label') in interesujace_klasy:
                        pasujace_jsony.append(file)
                        break  # wystarczy jedno trafienie
        except Exception as e:
            print(f"❌ Błąd przy przetwarzaniu {file}: {e}")

print("\n✅ JSON-y zawierające " + ", ".join(sorted(interesujace_klasy)) + ":")
for name in pasujace_jsony:
    print(name)
