import os
import re
from dotenv import load_dotenv
import requests
import mercantile
from vt2geojson.tools import vt_bytes_to_geojson
from concurrent.futures import ThreadPoolExecutor

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
ACCESS_TOKEN = os.getenv("MAPILLARY_TOKEN")
distance = float(os.getenv("AREA_DISTANCE", "0.0005"))

if not ACCESS_TOKEN:
    print("❌ MAPILLARY_TOKEN not provided.")
    exit(1)

# Load coordinates from file
if not os.path.exists("coordinates.txt"):
    print("⚠️ coordinates.txt not found.")

with open("coordinates.txt", "r") as f:
    coordinates_list = [line.strip() for line in f if line.strip()]

# Ustawienia
tile_coverage = 'mly1_public'
tile_layer = "image"
HEADERS = {'Authorization': f'OAuth {ACCESS_TOKEN}'}
session = requests.Session()

def download_image(image_id, image_url, destination):
    image_path = os.path.join(destination, f'{image_id}.jpg')
    if os.path.exists(image_path):
        print(f"Skipping {image_path} (already exists)")
        return

    try:
        response = session.get(image_url, timeout=10)
        if not response.ok:
            print(f"❌ Error downloading {image_id}: HTTP {response.status_code}")
            return

        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Downloaded {image_path}")
    except Exception as e:
        print(f"❌ Exception for {image_id}: {e}")

# Proces główny
for input_coords in coordinates_list:
    lat, lng = map(float, re.split(r"[/,]", input_coords))
    south, north = lat - distance, lat + distance
    west, east = lng - distance, lng + distance

    tiles = list(mercantile.tiles(west, south, east, north, 14))
    with ThreadPoolExecutor(max_workers=10) as executor:
        for tile in tiles:
            tile_url = f'https://tiles.mapillary.com/maps/vtp/{tile_coverage}/2/{tile.z}/{tile.x}/{tile.y}?access_token={ACCESS_TOKEN}'
            try:
                response = session.get(tile_url, timeout=10)
                if response.status_code != 200:
                    continue

                data = vt_bytes_to_geojson(response.content, tile.x, tile.y, tile.z, layer=tile_layer)
            except Exception as e:
                print(f"❌ Failed to load tile {tile}: {e}")
                continue

            for feature in data['features']:
                lng_feat, lat_feat = feature['geometry']['coordinates']
                if not (west < lng_feat < east and south < lat_feat < north):
                    continue

                sequence_id = feature['properties']['sequence_id']
                image_id = feature['properties']['id']
                destination = os.path.join("data", sequence_id)
                os.makedirs(destination, exist_ok=True)

                try:
                    url = f'https://graph.mapillary.com/{image_id}?fields=thumb_2048_url'
                    r = session.get(url, headers=HEADERS, timeout=10)
                    image_url = r.json().get('thumb_2048_url')
                    if image_url:
                        executor.submit(download_image, image_id, image_url, destination)
                except Exception as e:
                    print(f"❌ Failed to get image_url for {image_id}: {e}")
