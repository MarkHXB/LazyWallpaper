#! python3
# main.py - Simple wallpaper engine. Requests the wallpaper accordingly to weather, so if it snows then the
# application will fetch a snow picture.
# TODO: extra feature: add tags to four seasons, so if it snows, then parameters could be get like rocks, mountain, forest, etc..

# usage:
"""
- app starts
 + get user lat, long or city [weather.py] ✅
 + request weather api - should consume lat, long [weather.py] ✅
 + decision: current season, current weather type [ later: parameters ]⌛ [weather.py] ✅
 + request pexels api
 + use images - screen resolution doesnt matter because of windows 11
"""
from exceptions.tryToFetchDailyWallpapersException import TryToFetchDailyWallpapersException
from constants import *
import ctypes
import os

try:
    import pystray
    from PIL import Image
except ImportError:
    os.system("pip install pystray")
    os.system("pip install PIL")
    import pystray
    from PIL import Image

import weather
from pexels import get_daily_photos

from data import Data


def on_startup():
    #  1. get user lat, long or city [weather.py] ✅
    #  2. request weather api - should consume lat, long [weather.py] ✅
    #  3. decision: current season, current weather type [ later: parameters ]⌛ [weather.py] ✅
    #  4. get MAX_DAILIY_REQUESTS urls and persist it for later use, if its altered [pexels.py] ✅
    #  5. (if user has set wallpaper before, it should be loaded)[methodName], if not, (download the first one from the MAX_DAILIY_REQUESTS persist it and)[methodName] (setbg)[methodName] ⌛
    try:
        # load user config
        data.load_config()

        # get photo from pexels api and prepare it with arguments
        on_refresh()
    except Exception as ex:
        print(ex)


def on_next_bg():
    try:
        filepath = data.next_photo()
        ctypes.windll.user32.SystemParametersInfoW(20, 0, filepath, 0)
    except Exception as exc:
        raise exc


def on_prev_bg():
    try:
        filepath = data.prev_photo()
        ctypes.windll.user32.SystemParametersInfoW(20, 0, filepath, 0)
    except Exception as exc:
        print(exc)
        on_refresh()


def on_refresh():
    data.update_wallpapers(args=weather.get_weather_params(), fetch_api=get_daily_photos)


def on_exit():
    icon.stop()


def start_tray_app():
    # Create an icon image
    image = Image.open("../assets/icon.png")  # Replace with your icon image path
    menu = pystray.Menu(
        pystray.MenuItem('Download', on_startup),
        pystray.MenuItem('Next ✅', on_next_bg),
        pystray.MenuItem('Previous', on_prev_bg),
        pystray.MenuItem('──────────', lambda item: None),
        pystray.MenuItem('Exit', on_exit)
    )

    # Create the System Tray icon
    icon = pystray.Icon(APP_NAME, image, APP_NAME, menu)
    icon.run()


try:
    global data, icon
    data = Data()
    on_startup()
    try:
        start_tray_app()
    except TryToFetchDailyWallpapersException as exc:
        pass
except Exception as exc:
    print(exc)
