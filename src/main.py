#! python3
# main.py - Simple wallpaper engine. Requests the wallpaper accordingly to weather, so if it snows then the
# application will fetch a snow picture.
# TODO: extra feature: add tags to four seasons, so if it snows, then parameters could be get like rocks, mountain, forest, etc..

import menu
import os

from settings import Settings

try:
    import pystray
    from PIL import Image
except ImportError:
    os.system("pip install pystray")
    os.system("pip install PIL")
    import pystray
    from PIL import Image

from data import Data


try:
    settings = Settings()
    settings.load()

    data = Data(source=settings.current_source)
    menu.run(data, settings)
except Exception as exc:
    print(exc)
