import datetime
import os.path

from pypexels import PyPexels
from constants import *


def get_daily_photos(*args):
    py_pexel = PyPexels(API_KEY)
    photos = py_pexel.search(query=' '.join(args), per_page=MAX_DAILY_REQUESTS)
    res = []
    for p in photos.entries:
        og = p.src['original']
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        name = f'{timestamp}_{os.path.basename(og)}'
        filepath = f''
        res.append({'name': name, 'url': og, 'filepath': filepath})

    return res
# Help: https://pypexels.readthedocs.io/en/latest/classes/class_pypexels.html#pypexels-search-query-page-per-page
