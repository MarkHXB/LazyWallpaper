import ctypes

import pystray
from PIL import Image

import weather
from constants import *
from exceptions.sourceOfWallpapersIsEmptyException import SourceOfWallpapersIsEmptyException
from photos import get_daily_photos_from_pexels, get_daily_photos_from_unsplash


def run(data, settings):
    # Create an icon image
    icon = None
    max_tries_of_refetch = 1

    image = Image.open("../assets/icon.png")  # Replace with your icon image path
    menu = pystray.Menu(
        pystray.MenuItem('Next ', lambda item: on_next_bg(data, icon, max_tries_of_refetch)),
        pystray.MenuItem('Previous', lambda item: on_prev_bg(data, icon, max_tries_of_refetch)),
        pystray.MenuItem('──────────', lambda item: None),
        pystray.MenuItem(get_title_of_source(PEXELS_TITLE, data),
                         lambda item: on_change_source(PEXELS_TITLE, data, icon, settings)),
        pystray.MenuItem(get_title_of_source(UNSPLASH_TITLE, data),
                         lambda item: on_change_source(UNSPLASH_TITLE, data, icon, settings)),
        pystray.MenuItem('──────────', lambda item: None),
        pystray.MenuItem('Exit', lambda item: on_exit(icon))
    )

    # Create the System Tray icon
    icon = pystray.Icon(APP_NAME, image, APP_NAME, menu)
    icon.run()


def get_title_of_source(default, data):
    if data.source == default:
        return default + ' ✅'
    return default


# Events goes here...
def on_change_source(source, data, icon, settings):
    if source == PEXELS_TITLE:
        data.set_source(PEXELS_TITLE)
    elif source == UNSPLASH_TITLE:
        data.set_source(UNSPLASH_TITLE)

    # save settings
    settings.current_source = source
    settings.save()

    # init or load the source configs
    on_refresh(icon, data, source=source)


def on_refresh(icon, data, source=PEXELS_TITLE):
    # init or reload data object
    data.set_source(source)

    # declare source structure
    if data.source == PEXELS_TITLE:
        data.update_wallpapers(args=weather.get_weather_params(), fetch_api=get_daily_photos_from_pexels)
    elif data.source == UNSPLASH_TITLE:
        data.update_wallpapers(args=weather.get_weather_params(), fetch_api=get_daily_photos_from_unsplash)

    # load user config
    data.load()

    # update pystray menu
    icon.update_menu()


def on_next_bg(data, icon, max_tries_of_refetch):
    try:
        set_wallpaper(filepath=data.next_photo())
    except SourceOfWallpapersIsEmptyException:
        # try reload wallpapers
        if max_tries_of_refetch > 0:
            on_refresh(icon, data, data.source)
            max_tries_of_refetch -= 1
        else:
            icon.notify(message="Check if you have internet connection or restart Lazywallpaper.",
                        title="Something went wrong!")
    except Exception as exc:
        icon.notify(
            message="Check if you have internet connection or restart Lazywallpaper.\nFurther information: log.log",
            title="Something went wrong!")


def on_prev_bg(data, icon, max_tries_of_refetch):
    try:
        set_wallpaper(filepath=data.previos_photo())
    except SourceOfWallpapersIsEmptyException:
        # try reload wallpapers
        if max_tries_of_refetch > 0:
            on_refresh(icon, data, data.source)
            max_tries_of_refetch -= 1
        else:
            icon.notify(message="Check if you have internet connection or restart Lazywallpaper.",
                        title="Something went wrong!")
    except Exception as exc:
        icon.notify(
            message="Check if you have internet connection or restart Lazywallpaper.\nFurther information: log.log",
            title="Something went wrong!")


def set_wallpaper(filepath):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, filepath, 0)


def on_startup():
    #  1. get user lat, long or city [weather.py] ✅
    #  2. request weather api - should consume lat, long [weather.py] ✅
    #  3. decision: current season, current weather type [ later: parameters ]⌛ [weather.py] ✅
    #  4. get MAX_DAILIY_REQUESTS urls and persist it for later use, if its altered [photos.py] ✅
    #  5. (if user has set wallpaper before, it should be loaded)[methodName], if not, (download the first one from the MAX_DAILIY_REQUESTS persist it and)[methodName] (setbg)[methodName] ⌛
    try:
        # get photo from pexels api and prepare it with arguments
        on_refresh()
    except Exception as ex:
        print(ex)


def on_exit(icon):
    icon.stop()
