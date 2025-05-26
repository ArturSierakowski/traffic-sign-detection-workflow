import os
import sys
from datetime import timezone
import concurrent.futures
import requests
from requests.adapters import HTTPAdapter, Retry
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

if not MAPILLARY_TOKEN:
    print("❌ MAPILLARY_TOKEN not provided.")
    sys.exit(1)

if not SEQUENCE_IDS:
    print("⚠️ Brak sekwencji — pomijam pobieranie po sequence_id.")


session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
header = {'Authorization': f'OAuth {MAPILLARY_TOKEN}'}


def get_image_data(sequence_id):
    url = f'https://graph.mapillary.com/image_ids?sequence_id={sequence_id}'
    response = session.get(url, headers=header)
    if not response.ok:
        print(f"❌ Failed to fetch image list for sequence {sequence_id}")
        sys.exit(1)
    return response.json().get('data', [])


def get_image_details(image_id):
    fields = "creator,thumb_original_url,altitude,make,model,camera_type,captured_at,compass_angle,geometry,sequence"
    url = f'https://graph.mapillary.com/{image_id}?fields={fields}'
    response = session.get(url, headers=header)
    if not response.ok:
        print(f"❌ Failed to fetch image details for ID {image_id}")
        sys.exit(1)
    return response.json()


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
    response = session.get(url, stream=True, timeout=6)
    if not response.ok:
        print(f"❌ Failed to download image from {url}")
        return
    image = write_exif(response.content, metadata)
    with open(filepath, "wb") as f:
        f.write(image)
    print(f"✅ Downloaded: {filepath}")


for sequence_id in SEQUENCE_IDS:
    print(f"📦 Processing sequence {sequence_id}")
    image_ids = get_image_data(sequence_id)

    if not image_ids:
        print(f"⚠️ No images found for sequence {sequence_id}")
        continue

    destination = os.path.join("data", sequence_id)
    if os.path.exists(destination) and os.listdir(destination):
        print(f"⚠️ Sequence {sequence_id} already downloaded, skipping.")
        continue
    os.makedirs(destination, exist_ok=True)

    images_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_image_details, img['id']): img['id'] for img in image_ids}
        for future in concurrent.futures.as_completed(futures):
            image_data = future.result()
            if 'error' in image_data:
                continue
            image_data['sequence_id'] = sequence_id
            images_data.append(image_data)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for img_data in images_data:
            timestamp = datetime.fromtimestamp(int(img_data['captured_at']) / 1000, tz=timezone.utc).strftime('%Y-%m-%d_%HH%Mmn%Ss%f')[:-3]
            filename = f"{timestamp}.jpg"
            path = os.path.join(destination, filename)

            metadata = writer.PictureMetadata(
                capture_time=datetime.fromtimestamp(int(img_data['captured_at']) / 1000, tz=timezone.utc),
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
