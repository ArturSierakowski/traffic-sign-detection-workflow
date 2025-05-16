import os
from dotenv import load_dotenv
import requests
import mercantile
from vt2geojson.tools import vt_bytes_to_geojson

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
distance = float(os.getenv("AREA_DISTANCE", "0.0005"))

# Load coordinates from file
with open("coordinates.txt", "r") as f:
    coordinates_list = [line.strip() for line in f if line.strip()]

tile_coverage = 'mly1_public'
tile_layer = "image"

for input_coords in coordinates_list:
    lat, lng = map(float, input_coords.split("/"))
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
                os.makedirs(sequence_id, exist_ok=True)
                image_id = feature['properties']['id']
                header = {'Authorization': f'OAuth {ACCESS_TOKEN}'}
                url = f'https://graph.mapillary.com/{image_id}?fields=thumb_2048_url'
                r = requests.get(url, headers=header)
                image_url = r.json().get('thumb_2048_url')

                if image_url:
                    img_data = requests.get(image_url).content
                    with open(os.path.join(sequence_id, f'{image_id}.jpg'), 'wb') as handler:
                        handler.write(img_data)
