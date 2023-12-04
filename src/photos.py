import json
import uuid

import requests

from constants import *


def get_search_url(source_of_url, query, quantity):
    return f'{source_of_url}query={query}&per_page={quantity}&orientation=landscape'


def get_photos(source_of_url, header, query, quantity):
    url = get_search_url(source_of_url, query, quantity)
    header = {
        'Authorization': header
    }
    res = requests.get(url, headers=header)
    res.raise_for_status()
    return res.text


def get_daily_photos_from_pexels(args):
    photos = json.loads(get_photos(PEXELS_SEARCH_PHOTO_URL, PEXELS_API_HEADER, args, 5))['photos']
    res = []
    for p in photos:
        og = p['src']['original']
        name = str(uuid.uuid4())
        filepath = f''
        res.append({'name': name, 'url': og, 'filepath': filepath})

    return res


def get_daily_photos_from_unsplash(args):
    photos = json.loads(get_photos(UNSPLASH_PHOTO_URL, UNSPLASH_API_HEADER, args, 5))['results']
    res = []
    for p in photos:
        og = p['urls']['full']
        name = str(uuid.uuid4())
        filepath = f''
        res.append({'name': name, 'url': og, 'filepath': filepath})

    return res
