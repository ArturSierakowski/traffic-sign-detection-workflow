import json
import os

label_merge_map = {
    'A-6a': 'A-6',
    'A-6b': 'A-6',
    'A-6c': 'A-6',
    'A-6d': 'A-6',
    'A-6e': 'A-6',
    'A-6f': 'A-6',
    'A-9': 'A-9/10',
    'A-10': 'A-9/10',
    'A-11a': 'A-11',
    'A-12a': 'A-12',
    'A-12b': 'A-12',
    'A-12c': 'A-12',
    'A-18a': 'A-18',
    'A-18b': 'A-18',
    'A-22': 'A-22/23',
    'A-23': 'A-22/23',
    'B-15': 'B-15-19',
    'B-16': 'B-15-19',
    'B-17': 'B-5',
    'B-18': 'B-15-19',
    'B-19': 'B-15-19',
    'B-15/16': 'B-15-19', # tmp
    'B-18/19': 'B-15-19', # tmp
    'B-25': 'B-25/26',
    'B-26': 'B-25/26',
    'B-27': 'B-42',
    'B-28': 'B-42',
    'B-27/28': 'B-42',
    'B-34': 'B-42',
    'B-35': 'B-36',
    'C-13': 'C-13/16',
    'C-13a': 'C-13/16',
    'C-16': 'C-13/16',
    'D-4a': 'D-4',
    'D-4b': 'D-4',
    'D-6a': 'D-6',
    'D-6b': 'D-6',
    'D-11': 'D-11/12',
    'D-12': 'D-11/12',
    'D-13a': 'D-14',
    'D-13': 'D-14',
    'D-15': 'D-15/16/17',
    'D-16': 'D-15/16/17',
    'D-17': 'D-15/16/17',
    'D-18a': 'D-18',
    'D-18b': 'D-18',
    'D-23a': 'D-23-29',
    'D-26': 'D-23-29',
    'D-26b': 'D-23-29',
    'D-26c': 'D-23-29',
    'D-27': 'D-23-29',
    'D-28': 'D-23-29',
    'D-29': 'D-23-29',
    'D-41': 'D-40',
    'D-44': 'D-18',
    'D-46': 'D-46/52',
    'D-47': 'D-46/52',
    'D-52': 'D-46/52',
    'D-53': 'D-46/52',
    'G-1a': 'G-1',
    'G-1b': 'G-1',
    'G-1c': 'G-1',
    'G-1d': 'G-1',
    'G-1e': 'G-1',
    'G-1f': 'G-1',
    'G-3': 'G-3/4',
    'G-4': 'G-3/4',
    'F-1': 'F-1/2',
    'F-2': 'F-1/2',
    'F-2a': 'F-1/2',
    'F-5': 'F-5/6',
    'F-6': 'F-5/6',
    'F-8': 'DETOUR',
    'F-9': 'DETOUR',
    'F-14a': 'F-14',
    'F-14b': 'F-14',
    'F-14c': 'F-14',
    'F-15': 'F-10',
    'F-16': 'F-10',
    'F-17': 'F-10',
    'F-18': 'F-10',
    'F-19': 'F-10',
    'F-20': 'F-10',
    'F-21': 'DETOUR',
    'F-22': 'DETOUR',
    'F-21/22': 'DETOUR' # tmp
}

json_folder = "../dataset_prepared"

for filename in os.listdir(json_folder):
    if filename.endswith('.json'):
        file_path = os.path.join(json_folder, filename)

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for shape in data.get('shapes', []):
            old_label = shape['label']
            shape['label'] = label_merge_map.get(old_label, old_label)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

print("Ready: labels have been updated.")
