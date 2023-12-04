APP_NAME = 'LazyWallpaper'
MAX_DAILY_REQUESTS = 20
MAX_PHOTOS_ON_PC = 60 # avg size of 1 img: 7mb * 60q = 420MB
DATETIME_FORMAT = '%Y-%m-%d-%H:%M:%S'

# Pexels
PEXELS_API_KEY = '<your api key goes here>'
PEXELS_SEARCH_PHOTO_URL = 'https://api.pexels.com/v1/search?'
PEXELS_API_HEADER = PEXELS_API_KEY
PEXELS_TITLE = 'Pexels'

# Unsplash
UNSPLASH_TITLE = 'Unsplash'
UNSPLASH_API_KEY = '<your api key goes here>'
UNSPLASH_API_HEADER = f'Client-ID {UNSPLASH_API_KEY}'
UNSPLASH_PHOTO_URL = 'https://api.unsplash.com/search/photos?'