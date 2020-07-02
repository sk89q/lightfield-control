import importlib
import logging
import time

from PIL import Image, ImageFont, ImageDraw
from everett.manager import ConfigManager
from injector import inject, Injector, singleton

from lfcontrol.lightfield import LightField

logger = logging.getLogger(__name__)


@singleton
class ControlEngine:
    @inject
    def __init__(self, lightfield: LightField, config: ConfigManager, injector: Injector,
                 font: ImageFont):
        self.lightfield = lightfield
        self.displays = []
        self.font = font
        self.frame_duration = config('frame_duration', default='15', parser=float)

        for path in config('displays', default='', parser=lambda x: map(lambda x: x.strip(), x.split(','))):
            logger.info(f"Loading {path}...")
            last_period = path.rindex('.')
            module_path = path[:last_period]
            class_name = path[last_period + 1:]

            module = importlib.import_module(module_path)
            self.displays.append(injector.get(getattr(module, class_name)))

    def run(self):
        logger.info('Starting control engine...')
        while True:
            displays = self.displays[:]
            for display in displays:
                im = Image.new('RGB', (32, 8))
                draw = ImageDraw.Draw(im)
                try:
                    display.draw(im)
                except:
                    logger.error('Error drawing', exc_info=True)
                    draw.text((0, -2), "ERR ERR", font=self.font, fill=(255, 0, 0, 255))
                try:
                    self.lightfield.draw(im)
                except:
                    logger.error('Drawing sending data', exc_info=True)
                time.sleep(self.frame_duration)
