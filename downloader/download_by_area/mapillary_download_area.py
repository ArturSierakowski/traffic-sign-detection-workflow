import os
import re
from dotenv import load_dotenv
import requests
import mercantile
from vt2geojson.tools import vt_bytes_to_geojson

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
ACCESS_TOKEN = os.getenv("MAPILLARY_TOKEN")
distance = float(os.getenv("AREA_DISTANCE", "0.0005"))

# Load coordinates from file
with open("coordinates.txt", "r") as f:
    coordinates_list = [line.strip() for line in f if line.strip()]

tile_coverage = 'mly1_public'
tile_layer = "image"

for input_coords in coordinates_list:
    lat, lng = map(float, re.split(r"[/,]", input_coords))
    south, north = lat - distance, lat + distance
    west, east = lng - distance, lng + distance

    tiles = list(mercantile.tiles(west, south, east, north, 14))
    for tile in tiles:
        tile_url = f'https://tiles.mapillary.com/maps/vtp/{tile_coverage}/2/{tile.z}/{tile.x}/{tile.y}?access_token={ACCESS_TOKEN}'
        response = requests.get(tile_url)
        if response.status_code != 200:
            continue

        data = vt_bytes_to_geojson(response.content, tile.x, tile.y, tile.z, layer=tile_layer)
        for feature in data['features']:
            lng_feat, lat_feat = feature['geometry']['coordinates']
            if west < lng_feat < east and south < lat_feat < north:
                sequence_id = feature['properties']['sequence_id']
                destination = os.path.join("data", sequence_id)
                try:
                    os.makedirs(destination, exist_ok=False)
                    print(f"📂 Created folder: {destination}")
                except FileExistsError:
                    pass

                image_id = feature['properties']['id']
                header = {'Authorization': f'OAuth {ACCESS_TOKEN}'}
                url = f'https://graph.mapillary.com/{image_id}?fields=thumb_2048_url'
                r = requests.get(url, headers=header)
                image_url = r.json().get('thumb_2048_url')

                if image_url:
                    img_data = requests.get(image_url).content
                    image_path = os.path.join(destination, f'{image_id}.jpg')
                    if os.path.exists(image_path):
                        print(f"Skipping {image_path} (already exists)")
                        continue

                    with open(image_path, 'wb') as handler:
                        handler.write(img_data)
