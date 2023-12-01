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
    #  4. get MAX_DAILIY_REQUESTS urls and persist it for later use, if its altered [pexels.py] ⌛
    #  5. (if user has set wallpaper before, it should be loaded)[methodName], if not, (download the first one from the MAX_DAILIY_REQUESTS persist it and)[methodName] (setbg)[methodName] ⌛
    try:
        # Init data
        data = Data()
        data.load_config()

        # Data validation
        if not data.isValid():
            raise Exception('User data is not valid, User exceeded daily quote')

        # 4.
        # get photo from pexels api and prepare it with arguments
        if data.should_update_daily_wallpapers():
            data.wallpapers = get_daily_photos('wallpaper', weather.get_weather_params())
            data.save_config()

        on_next_bg(data)

        # persist photo to hard drive and edit data layer
        # filepath = data.save_photo(photo)

    except Exception as ex:
        print(ex)


def on_next_bg(data):
    filepath = data.next_photo()
    ctypes.windll.user32.SystemParametersInfoW(20, 0, filepath, 0)


def on_prev_bg(data):
    p = data.previous_photo()
    # ctypes.windll.user32.SystemParametersInfoW(20, 0, p.filepath, 0)


def on_exit():
    pass


# Function to be triggered when the icon is clicked
"""
def on_clicked(icon, item):
    print(f'Clicked {item}')

# Create an icon image
image = Image.open("icon.png")  # Replace with your icon image path
menu = pystray.Menu(
    pystray.MenuItem('Item 1', on_clicked),
    pystray.MenuItem('Item 2', on_clicked),
    pystray.MenuItem('Item 3', on_clicked)
)

# Create the System Tray icon
icon = pystray.Icon("MyApp", image, "My App", menu)
icon.run()
icon.notify("Valami", "asdasdsa")
"""

on_startup()
