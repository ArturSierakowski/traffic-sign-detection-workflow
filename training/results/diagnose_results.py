import re

# Ścieżka do pliku z wynikami YOLO
file_path = "results.txt"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

pattern = re.compile(r"^\s+([A-Z0-9\-\/]+)\s+\d+\s+\d+\s+[\d\.]+\s+([\d\.]+)", re.MULTILINE)

slabe_klasy = []
for match in pattern.finditer(text):
    klasa, map50 = match.groups()
    if float(map50) < 0.6:
        slabe_klasy.append((klasa, float(map50)))

# Sortowanie i wypisanie
slabe_klasy.sort(key=lambda x: x[1])
print("📉 Classes with bad mAP50 (< 0.6):\n")
for klasa, score in slabe_klasy:
    print(f"{klasa:<10} → mAP50 = {score:.3f}")
