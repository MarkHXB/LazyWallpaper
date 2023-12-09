import datetime
import json
import os.path

from exceptions.sourceOfWallpapersIsEmptyException import SourceOfWallpapersIsEmptyException
from constants import *

try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests


class Data:
    filename = 'user.json'

    def __init__(self, last_request_time=datetime.datetime.now().strftime(DATETIME_FORMAT), current_day_requests=0,
                 wallpapers=[], current_wallpaper_id=0, source=PEXELS_TITLE):
        self.last_request_time = last_request_time
        self.current_day_requests = current_day_requests  # per photo
        self.wallpapers = wallpapers
        self.current_wallpaper_id = current_wallpaper_id
        self.source = source
        self.data_filepath = os.path.join(APP_FOLDER, self.source, self.filename)
        self.photos_folder = os.path.join(APP_FOLDER, self.source, 'photos')

    def to_dict(self):
        return {
            'last_request_time': self.last_request_time,
            'current_day_requests': self.current_day_requests,
            'wallpapers': self.wallpapers,
            'current_wallpaper_id': self.current_wallpaper_id,
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
                self.current_wallpaper_id = data['current_wallpaper_id']

                # check whether the limited count of photos is full
                if os.path.isdir(self.photos_folder):
                    if self._count_of_files_in_folder() >= MAX_FILES_TO_STORE:
                        files_to_delete = self._get_oldest_filepaths()
                        for f in files_to_delete:
                            try:
                                os.remove(f)
                            except OSError as e:
                                print(f'Cant delete file: {e}')
        except Exception as exc:
            raise exc

    def save(self):
        try:
            if not os.path.isfile(self.data_filepath):
                self._init()
            with open(self.data_filepath, 'w') as file:
                json.dump(self.to_dict(), file)
        except Exception as exc:
            raise exc

    def save_photo(self):
        try:
            p = self.get_current_photo()
            if not p:
                raise Exception(f'Photo not found!')

            # download img by url
            url = p['url']
            filepath = p['filepath']
            header = None
            if self.source == PEXELS_TITLE:
                header = {'Authorization': PEXELS_API_HEADER}
            elif self.source == UNSPLASH_TITLE:
                header = {'Authorization': UNSPLASH_API_HEADER}
            res = requests.get(url, headers=header)
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
            self.save()

            return filepath

        except Exception as ex:
            print(ex)

    def next_photo(self):
        try:
            if self.wallpapers:
                # init
                if not self.current_wallpaper_id:
                    self.current_wallpaper_id = self.wallpapers[0]['id']
                else:  # get next
                    # get index from wallpapers where name equals
                    idx = next((i for i, wp in enumerate(self.wallpapers) if wp['id'] == self.current_wallpaper_id),
                               None)

                    if idx is None:
                        # replace this shitty code
                        self.current_wallpaper_id = self.wallpapers[0]['id']
                    elif idx + 1 >= len(self.wallpapers):
                        # start from beginning
                        self.current_wallpaper_id = self.wallpapers[0]['id']
                    else:
                        self.current_wallpaper_id = self.wallpapers[idx + 1]['id']
            else:
                raise SourceOfWallpapersIsEmptyException(f'called through next_photo')
        except Exception as exc:
            raise exc

        self.save()

        if os.path.isfile((p := self.get_current_photo()['filepath'])):
            return p
        else:
            if self.isValid():
                return self.save_photo()

    def get_current_photo(self):
        if self.current_wallpaper_id is not None:
            for p in self.wallpapers:
                if p['id'] == self.current_wallpaper_id:
                    return p
        return None

    def previous_photo(self):
        try:
            if self.wallpapers:
                # init
                last = len(self.wallpapers) - 1
                if not self.current_wallpaper_id:
                    self.current_wallpaper_id = self.wallpapers[last]['id']
                else:  # get next
                    # get index from wallpapers where name equals
                    idx = next((i for i, wp in enumerate(self.wallpapers) if wp['id'] == self.current_wallpaper_id),
                               None)

                    if idx is None:
                        # replace this shitty code
                        self.current_wallpaper_id = self.wallpapers[last]['id']
                    elif idx - 1 < 0:
                        # start from beginning
                        self.current_wallpaper_id = self.wallpapers[last]['id']
                    else:
                        self.current_wallpaper_id = self.wallpapers[idx - 1]['id']
            else:
                raise SourceOfWallpapersIsEmptyException(f'called through next_photo')
        except Exception as exc:
            raise exc

        self.save()

        if os.path.isfile((p := self.get_current_photo()['filepath'])):
            return p
        else:
            if self.isValid():
                return self.save_photo()

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

    def _count_of_files_in_folder(self):
        files = os.listdir(self.photos_folder)
        file_count = 0

        for file in files:
            file_path = os.path.join(self.photos_folder, file)
            if os.path.isfile(file_path):
                file_count += 1
        return file_count

    def _get_oldest_filepaths(self):
        if self.wallpapers is None or MAX_DAILY_REQUESTS < 1 or len(self.wallpapers) < MAX_DAILY_REQUESTS:
            return

        dates = [d['added_time'] for d in self.wallpapers]
        sorted_dates = dates.sort(reverse=True)
        return sorted_dates[:MAX_DAILY_REQUESTS]

    def get_page_of_day(self):
        # second check to avoid resulting fractional numbers
        if self.wallpapers is None or len(self.wallpapers) < QUANTITY_OF_DOWNLOADS_PER_PAGE:
            return 1

        if len(self.wallpapers) == QUANTITY_OF_DOWNLOADS_PER_PAGE:
            return 2

        if QUANTITY_OF_DOWNLOADS_PER_PAGE == 0:
            raise Exception('QUANTITY_OF_DOWNLOADS_PER_PAGE must not be 0.')

        return (len(self.wallpapers) / QUANTITY_OF_DOWNLOADS_PER_PAGE) + 1

    def update_wallpapers(self, args, fetch_api):
        if not fetch_api:
            raise Exception('Fetch api not found to update wallpapers.')
        w = fetch_api(args=args, source=self.source, page=self.get_page_of_day())
        if not w:
            raise Exception('Not found any newer version of photos for today.')

        for p in w:
            self.wallpapers.append(p)
        self.save()

    def set_source(self, source):
        self.source = source
        self.data_filepath = os.path.join(APP_FOLDER, self.source, self.filename)
        self.photos_folder = os.path.join(APP_FOLDER, self.source, 'photos')
