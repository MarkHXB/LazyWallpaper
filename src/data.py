import datetime
import json
import os.path

from exceptions.tryToFetchDailyWallpapersException import TryToFetchDailyWallpapersException
from constants import *

try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests


class Data:
    filename = 'user.json'
    user_home = os.getcwd()
    app_folder = os.path.dirname(os.path.abspath(__file__))
    data_filepath = os.path.join(app_folder, filename)
    photos_folder = os.path.join(app_folder, 'photos')
    config_loaded = False

    def __init__(self, last_request_time=datetime.datetime.now().strftime(DATETIME_FORMAT), current_day_requests=0,
                 wallpapers=[], current_wallpaper_name=''):
        self.last_request_time = last_request_time
        self.current_day_requests = current_day_requests  # per photo
        self.wallpapers = wallpapers
        self.current_wallpaper_name = current_wallpaper_name

    def to_dict(self):
        return {
            'last_request_time': self.last_request_time,
            'current_day_request': self.current_day_requests,
            'wallpapers': self.wallpapers,
            'current_wallpaper_name': self.current_wallpaper_name,
        }

    def load_config(self):
        try:
            if not os.path.isfile(self.filename):
                self.init_config_file()
            with open(self.data_filepath, 'r') as file:
                data = json.load(file)
                self.last_request_time = data['last_request_time']
                self.current_day_request = data['current_day_request']
                self.wallpapers = data['wallpapers']
                self.current_wallpaper_name = data['current_wallpaper_name']
        except Exception as exc:
            print(exc)

    def save_config(self):
        try:
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
            res = requests.get(url, headers=API_HEADER)
            res.raise_for_status()

            # prepare img for saving
            self.current_day_requests += 1
            self.last_request_time = datetime.datetime.now().strftime(DATETIME_FORMAT)

            # write img to drive
            if not os.path.exists(self.photos_folder):
                os.makedirs(self.photos_folder)
            with open(filepath, 'wb') as file:
                for chunk in res.iter_content(100000):
                    file.write(chunk)

            # save changes
            self.save_config()

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
                raise TryToFetchDailyWallpapersException("from next_photo")
        except Exception as exc:
            print(exc)

        self.save_config()

        if not os.path.isfile(p['filepath']):
            return self.save_photo(p)
        else:
            return p['filepath']

    def isValid(self):
        self.load_config()  # maybe store
        return self.current_day_requests < MAX_DAILY_REQUESTS

    def init_config_file(self):
        # isValid
        # load photos by requests
        try:
            with open(self.data_filepath, 'w') as file:
                json.dump(self.to_dict(), file)
        except Exception as exc:
            print(exc)

    def should_update_daily_wallpapers(self):
        date = datetime.datetime.strptime(self.last_request_time, DATETIME_FORMAT)
        date += datetime.timedelta(days=1)
        return datetime.datetime.now() >= date and self.isValid()

    def update_wallpapers(self, args, fetch_api):
        # if not self.should_update_daily_wallpapers():
        #    raise Exception('Wallpapers cannot be refreshed, because either user exceeded daily download limit or not waited 24 hours.')
        if not fetch_api:
            raise Exception('Fetch api not found to update wallpapers.')
        w = fetch_api(args)
        if not w:
            raise Exception('Not found any newer version of photos for today.')

        self.wallpapers = w
        self.save_config()


