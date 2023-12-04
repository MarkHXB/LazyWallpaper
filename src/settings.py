import json
import os

from constants import PEXELS_TITLE


class Settings:
    filename = 'settings.json'
    app_folder = os.path.dirname(os.path.abspath(__file__))
    settings_filepath = os.path.join(app_folder, filename)

    def __init__(self, current_source = PEXELS_TITLE):
        self.current_source = current_source

    def to_dict(self):
        return {
            'current_source': self.current_source
        }

    def load(self):
        try:
            if not os.path.isfile(self.settings_filepath):
                self._init()
            with open(self.settings_filepath, 'r') as file:
                data = json.load(file)
                self.current_source = data['current_source']
        except Exception as exc:
            print(exc)

    def save(self):
        try:
            with open(self.settings_filepath, 'w') as file:
                json.dump(self.to_dict(), file)
        except Exception as exc:
            print(exc)

    def _init(self):
        try:
            # init work folder if not exists
            directory = os.path.dirname(self.settings_filepath)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(self.settings_filepath, 'w') as file:
                json.dump(self.to_dict(), file)
        except Exception as exc:
            print(exc)