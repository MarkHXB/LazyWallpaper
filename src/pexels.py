import datetime
import json
import os.path
import requests

from constants import *

def get_search_url(query, quantity):
    return f'{SEARCH_PHOTO_URL}query={query}&per_page={quantity}&orientation=landscape'


def get_photos(query, quantity):
    url = get_search_url(query, quantity)
    res = requests.get(url, headers=API_HEADER)
    res.raise_for_status()
    return res.text


def get_daily_photos(args):
    photos = json.loads(get_photos(args, 5))['photos']
    res = []
    for p in photos:
        og = p['src']['original']
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        name = f'{timestamp}_{os.path.basename(og)}'
        filepath = f''
        res.append({'name': name, 'url': og, 'filepath': filepath})

    return res
# Help: https://pypexels.readthedocs.io/en/latest/classes/class_pypexels.html#pypexels-search-query-page-per-page