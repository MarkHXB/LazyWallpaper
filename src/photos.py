import json
import os
from urllib.parse import urlparse

import requests

from constants import *


def _get_search_url(source_of_url, query, page, quantity):
    return f'{source_of_url}query={query}&page={page}&per_page={quantity}&orientation=landscape'


def _get_photos(source_of_url, header, query, page, quantity):
    url = _get_search_url(source_of_url, query, page, quantity)
    header = {
        'Authorization': header
    }
    res = requests.get(url, headers=header)
    res.raise_for_status()
    return res


def _get_single_photo_by_id(source_of_url, header, id):
    url = f'{source_of_url}{id}'
    header = {
        'Authorization': header
    }
    res = requests.get(url, headers=header)
    res.raise_for_status()
    return res.text


def get_daily_photos_from_pexels(args, source, page):
    res = _get_photos(PEXELS_SEARCH_PHOTO_URL, PEXELS_API_HEADER, args, page, QUANTITY_OF_DOWNLOADS_PER_PAGE)
    photos = json.loads(res.text)['photos']
    result = []
    for p in photos:
        id = p['id']
        url = p['src']['original']
        filepath = get_file_path(res, url, source, str(id))
        result.append({'id': id, 'url': url, 'filepath': filepath})

    return result


def get_daily_photos_from_unsplash(args, source, page):
    res = _get_photos(UNSPLASH_PHOTO_URL, UNSPLASH_API_HEADER, args, page, QUANTITY_OF_DOWNLOADS_PER_PAGE)
    photos = json.loads(res.text)['results']
    result = []
    for p in photos:
        id = p['id']
        url = p['urls']['full']
        filepath = get_file_path(res, url, source, str(id))
        result.append({'id': id, 'url': url, 'filepath': filepath})

    return result


def get_file_path(res, url, source, filename):
    return os.path.join(APP_FOLDER, source, 'photos', f'{filename}.{get_ext(res, url, source)}')


def get_ext(res, url, source):
    if source == PEXELS_TITLE:
        if not str(url).endswith(('.jpg', '.jpeg', '.png')):
            # get extension from content-type
            content_type = res.headers.get('content-type')
            ext = content_type.split('/')[1]
            return ext
        return url.split('.')[-1]
    elif source == UNSPLASH_TITLE:
        params = url.split('?')[1].split('&')
        for param in params:
            if 'fm=' in param:
                file_format = param.split('=')[1]
                return file_format
