import os

APP_NAME = 'LazyWallpaper'
MAX_DAILY_REQUESTS = 20
MAX_FILES_TO_STORE = 20
DATETIME_FORMAT = '%Y-%m-%d-%H:%M:%S'
QUANTITY_OF_DOWNLOADS_PER_PAGE = 5

# Pexels
PEXELS_API_KEY = 'RPZYlY7tKTlg38IanAXSByLazHrdjwU5pJKFuhxrd3eUA2hUoaCQTzob'
PEXELS_SEARCH_PHOTO_URL = 'https://api.pexels.com/v1/search?'
PEXELS_API_HEADER = PEXELS_API_KEY
PEXELS_TITLE = 'Pexels'

# Unsplash
UNSPLASH_TITLE = 'Unsplash'
UNSPLASH_API_KEY = 'gyvkX6uoWQoRATsa4j2V6efNTdu5Gyu8-KIVyWqbOFk'
UNSPLASH_API_HEADER = f'Client-ID {UNSPLASH_API_KEY}'
UNSPLASH_PHOTO_URL = 'https://api.unsplash.com/search/photos?'
UNSPLASH_PHOTO_URL_BY_ID = 'https://api.unsplash.com/photos/'

# Data
APP_FOLDER = os.path.dirname(os.path.abspath(__file__))
