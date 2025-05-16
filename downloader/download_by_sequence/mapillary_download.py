import requests
from requests.adapters import HTTPAdapter, Retry
import os
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv
import writer
from model import PictureType

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
MAPILLARY_TOKEN = os.getenv("MAPILLARY_TOKEN")

sequences_file = "sequences.txt"
if os.path.exists(sequences_file):
    with open(sequences_file, "r", encoding="utf-8") as f:
        SEQUENCE_IDS = [line.strip() for line in f if line.strip()]
else:
    SEQUENCE_IDS = []

if not MAPILLARY_TOKEN or not SEQUENCE_IDS:
    print("❌ MAPILLARY_TOKEN or sequences.txt not provided.")
    exit(1)

session = requests.Session()
session.mount('https://', HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1, status_forcelist=[429, 502, 503, 504])))

def get_image_data(sequence_id, header):
    url = f'https://graph.mapillary.com/image_ids?sequence_id={sequence_id}'
    r = requests.get(url, headers=header)
    data = r.json()
    return data.get('data', [])

def get_image_details(image_id, header):
    fields = "creator,thumb_original_url,altitude,make,model,camera_type,captured_at,compass_angle,geometry,sequence"
    url = f'https://graph.mapillary.com/{image_id}?fields={fields}'
    r = requests.get(url, headers=header)
    return r.json()

def write_exif(picture, metadata):
    with writer.Writer(picture) as img:
        img.add_artist(metadata)
        img.add_camera_make(metadata)
        img.add_camera_model(metadata)
        img.add_datetimeoriginal(metadata)
        img.add_lat_lon(metadata)
        img.add_altitude(metadata)
        img.add_direction(metadata)
        img.add_img_projection(metadata)
        img.apply()
        return img.get_Bytes()

def download_image(url, filepath, metadata):
    with open(filepath, "wb") as f:
        r = session.get(url, stream=True, timeout=6)
        image = write_exif(r.content, metadata)
        f.write(image)
    print(f"✅ Downloaded: {filepath}")

header = {'Authorization': f'OAuth {MAPILLARY_TOKEN}'}
for sequence_id in SEQUENCE_IDS:
    print(f"📦 Processing sequence {sequence_id}")
    image_ids = get_image_data(sequence_id, header)

    if not image_ids:
        print(f"⚠️  No images found for sequence {sequence_id}")
        continue

    destination = os.path.join("data", sequence_id)
    os.makedirs(destination, exist_ok=True)

    images_data = []
    for img in image_ids:
        image_data = get_image_details(img['id'], header)
        if 'error' in image_data:
            continue
        image_data['sequence_id'] = sequence_id
        images_data.append(image_data)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for img_data in images_data:
            timestamp = datetime.utcfromtimestamp(int(img_data['captured_at']) / 1000).strftime('%Y-%m-%d_%HH%Mmn%Ss%f')[:-3]
            filename = f"{timestamp}.jpg"
            path = os.path.join(destination, filename)

            metadata = writer.PictureMetadata(
                capture_time=datetime.utcfromtimestamp(int(img_data['captured_at']) / 1000),
                artist=img_data['creator']['username'],
                camera_make=img_data['make'],
                camera_model=img_data['model'],
                longitude=img_data['geometry']['coordinates'][0],
                latitude=img_data['geometry']['coordinates'][1],
                picture_type=PictureType("equirectangular") if img_data.get('camera_type') in ['spherical', 'equirectangular'] else PictureType("flat"),
                direction=img_data['compass_angle'],
                altitude=img_data['altitude']
            )

            executor.submit(download_image, img_data['thumb_original_url'], path, metadata)
