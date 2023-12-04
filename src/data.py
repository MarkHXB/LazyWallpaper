import datetime
import json
import os.path
from urllib.parse import urlparse

from exceptions.sourceOfWallpapersIsEmptyException import SourceOfWallpapersIsEmptyException
from constants import *

try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests


class Data:
    filename = 'user.json'
    app_folder = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, last_request_time=datetime.datetime.now().strftime(DATETIME_FORMAT), current_day_requests=0,
                 wallpapers=[], current_wallpaper_name='', source=PEXELS_TITLE):
        self.last_request_time = last_request_time
        self.current_day_requests = current_day_requests  # per photo
        self.wallpapers = wallpapers
        self.current_wallpaper_name = current_wallpaper_name
        self.source = source
        self.data_filepath = os.path.join(self.app_folder, self.source, self.filename)
        self.photos_folder = os.path.join(self.app_folder, self.source, 'photos')

    def to_dict(self):
        return {
            'last_request_time': self.last_request_time,
            'current_day_requests': self.current_day_requests,
            'wallpapers': self.wallpapers,
            'current_wallpaper_name': self.current_wallpaper_name,
        }

    def load(self):
        try:
            if not os.path.isfile(self.data_filepath):
                self._init()
            with open(self.data_filepath, 'r') as file:
                data = json.load(file)
                self.last_request_time = data['last_request_time']
                self.current_day_requests = data['current_day_requests']
                self.wallpapers = data['wallpapers']
                self.current_wallpaper_name = data['current_wallpaper_name']
        except Exception as exc:
            print(exc)

    def save(self):
        try:
            if not os.path.isfile(self.data_filepath):
                self._init()
            with open(self.data_filepath, 'w') as file:
                json.dump(self.to_dict(), file)
        except Exception as exc:
            print(exc)

    def save_photo(self, photo):
        try:
            if not photo:
                raise Exception(f'Photo not found!')

            # download img by url
            url = photo['url']
            name = photo['name']
            filepath = photo['filepath']
            header = None
            if self.source == PEXELS_TITLE:
                header = {'Authorization': PEXELS_API_HEADER}
            elif self.source == UNSPLASH_TITLE:
                header = {'Authorization': UNSPLASH_API_HEADER}
            res = requests.get(url, headers=header)
            res.raise_for_status()

            # prepare img for saving
            if not str(url).endswith(('.jpg', '.jpeg', '.png')):
                # get extension from content-type
                content_type = res.headers.get('content-type')
                ext = content_type.split('/')[1]
                parsed_filepath = os.path.abspath(urlparse(filepath).path)
                filepath = rf'{parsed_filepath}.{ext}'
            else:
                if not filepath.endswith(('.jpg', '.jpeg', '.png')):
                    ext = url.split('.')[-1]
                    filepath = rf'{filepath}.{ext}'

            self.current_day_requests += 1
            self.last_request_time = datetime.datetime.now().strftime(DATETIME_FORMAT)

            # write img to drive
            if not os.path.exists(self.photos_folder):
                os.makedirs(self.photos_folder)
            with open(filepath, 'wb') as file:
                for chunk in res.iter_content(100000):
                    file.write(chunk)

            # save changes
            self.save()

            return filepath

        except Exception as ex:
            print(ex)

    def next_photo(self):
        p = None
        try:
            if self.wallpapers:
                # init
                if not self.current_wallpaper_name:
                    p = self.wallpapers[0]
                    self.current_wallpaper_name = p['name']
                    p['filepath'] = os.path.join(self.photos_folder, self.current_wallpaper_name)
                else:  # get next
                    # get index from wallpapers where name equals
                    idx = next((i for i, wp in enumerate(self.wallpapers) if wp['name'] == self.current_wallpaper_name),
                               None)

                    if idx is None:
                        # replace this shitty code
                        p = self.wallpapers[0]
                        self.current_wallpaper_name = p['name']
                        p['filepath'] = os.path.join(self.photos_folder, self.current_wallpaper_name)
                    elif idx + 1 >= len(self.wallpapers):
                        # start from beginning
                        p = self.wallpapers[0]
                        self.current_wallpaper_name = p['name']
                        p['filepath'] = os.path.join(self.photos_folder, self.current_wallpaper_name)
                    else:
                        p = self.wallpapers[idx + 1]
                        self.current_wallpaper_name = p['name']
                        p['filepath'] = os.path.join(self.photos_folder, self.current_wallpaper_name)
            else:
                raise SourceOfWallpapersIsEmptyException(f'called through next_photo')
        except Exception as exc:
            raise exc

        self.save()

        if not os.path.isfile(p['filepath']) and self.isValid():
            return self.save_photo(p)
        else:
            return p['filepath']

    def isValid(self):
        self.load()  # maybe store
        return self.current_day_requests < MAX_DAILY_REQUESTS

    def _init(self):
        try:
            # init work folder if not exists
            directory = os.path.dirname(self.data_filepath)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(self.data_filepath, 'w') as file:
                json.dump(self.to_dict(), file)
        except Exception as exc:
            print(exc)

    def should_update_daily_wallpapers(self):
        date = datetime.datetime.strptime(self.last_request_time, DATETIME_FORMAT)
        date += datetime.timedelta(days=1)
        return datetime.datetime.now() >= date

    def update_wallpapers(self, args, fetch_api):
        # if not self.should_update_daily_wallpapers():
        #    raise Exception('Wallpapers cannot be refreshed, because either user exceeded daily download limit or not waited 24 hours.')
        if not fetch_api:
            raise Exception('Fetch api not found to update wallpapers.')
        w = fetch_api(args)
        if not w:
            raise Exception('Not found any newer version of photos for today.')

        self.wallpapers = w
        self.save()

    def set_source(self, source):
        self.source = source
        self.data_filepath = os.path.join(self.app_folder, self.source, self.filename)
        self.photos_folder = os.path.join(self.app_folder, self.source, 'photos')
