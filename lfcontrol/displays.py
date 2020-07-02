import io
import pkgutil

import requests
from PIL import ImageFont, ImageDraw, Image
from everett.manager import ConfigManager
from injector import inject
from pickledb import PickleDB

from lfcontrol.cache import CachedData


class Display:
    def draw(self, im):
        pass


class Forecast(Display):
    @inject
    def __init__(self, font: ImageFont, config: ConfigManager, db: PickleDB):
        self.font = font
        self.api_key = config('darksky_api_key')
        self.coords = config('weather_coords').replace(' ', '')
        self.icons = {k: Image.open(io.BytesIO(pkgutil.get_data("lfcontrol", f"icons/weather/{v}"))) for k, v in {
            "clear-day": "clear.png",
            "clear-night": "clear.png",
            "rain": "rain.png",
            "snow": "snow.png",
            "sleet": "snow.png",
            "wind": "wind.png",
            "fog": "cloudy.png",
            "cloudy": "cloudy.png",
            "partly-cloudy-day": "partly_cloudy.png",
            "partly-cloudy-night": "partly_cloudy.png",
        }.items()}
        self.data = CachedData(self.fetch_data, db, 'forecast', 60 * 60)

    def fetch_data(self):
        return requests.get(f'https://api.darksky.net/forecast/{self.api_key}/{self.coords}').json()

    def draw(self, im):
        forecast = self.data.get()["daily"]["data"][0]
        draw = ImageDraw.Draw(im)
        icon = self.icons.get(forecast["icon"], None)
        if icon:
            im.paste(icon, (2, 0))
        draw.text((13, 0), str(round(forecast["apparentTemperatureHigh"])),
                  font=self.font, fill=(255, 255, 255, 255))
        draw.text((22, 0), str(round(forecast["apparentTemperatureLow"])),
                  font=self.font, fill=(100, 0, 255, 255))


class USACovidCaseCount(Display):
    @inject
    def __init__(self, font: ImageFont, config: ConfigManager, db: PickleDB):
        self.font = font
        self.db = db
        self.uid = config('covid_usa_cases_uid', default='0', parser=int)
        self.data = None
        self.bg = Image.open(io.BytesIO(pkgutil.get_data("lfcontrol", "bg/covid.png")))
        self.data = CachedData(self.fetch_data, db, 'covid_usa_cases_data', 60 * 60)

    def fetch_data(self):
        return requests.get('https://covid19.mathdro.id/api/countries/USA/confirmed').json()

    def draw(self, im):
        draw = ImageDraw.Draw(im)
        im.paste(self.bg, (0, 0))
        found = False
        for row in self.data.get():
            if row['uid'] == self.uid:
                draw.text((0, 1), f"{row['confirmed']}", font=self.font, fill=(255, 100, 0, 255))
                found = True
                break
        if not found:
            draw.text((0, 1), f"???", font=self.font, fill=(255, 100, 0, 255))
