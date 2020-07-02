from struct import pack

import requests
from everett.manager import ConfigManager
from injector import inject, singleton

import logging

logger = logging.getLogger(__name__)


@singleton
class LightField:
    @inject
    def __init__(self, config: ConfigManager):
        self.url = config('url', default='http://192.168.0.1', doc='Instance URL')
        self.opacity = config('opacity', default='0.2', parser=float, doc='0 to 1')

    def configure_wifi_ap(self, ssid, password):
        logger.info("Sending configuration payload...")
        requests.post(f'{self.url}/api/v1/wifi/ap/', params={
            "ssid": ssid,
            "password": password,
        })
        logger.info("Completed configuration")

    def configure_wifi_client(self, ssid, password):
        logger.info("Sending configuration payload...")
        requests.post(f'{self.url}/api/v1/wifi/client/', params={
            "ssid": ssid,
            "password": password,
        })
        logger.info("Completed configuration")

    def image_to_payload(self, im, opacity):
        data = b''
        for i in range(256):
            x = i // 8
            y = i % 8
            r, g, b = im.getpixel((x, y if x % 2 == 0 else 7 - y))
            data += pack('BBB', int(r * opacity), int(g * opacity), int(b * opacity))
        return data

    def draw(self, im):
        requests.post(f'{self.url}/api/v1/program/', params={
            "program": "image",
        })

        requests.post(f'{self.url}/api/v1/programs/image/', files={
            's': self.image_to_payload(im, self.opacity)
        })
