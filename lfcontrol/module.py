import io
import os
import pkgutil

import pickledb
from PIL import ImageFont
from everett.ext.inifile import ConfigIniEnv
from everett.manager import ConfigManager, ConfigOSEnv
from injector import Module, singleton, provider


class ControlModule(Module):
    @singleton
    @provider
    def provide_config(self) -> ConfigManager:
        return ConfigManager(
            environments=[
                ConfigOSEnv(),
                ConfigIniEnv([
                    os.environ.get('LFCONTROL_CONFIG'),
                    '~/.lfcontrol.ini',
                    '.lfcontrol.ini',
                    '/etc/lfcontrol.ini',
                ]),
            ],
        ).with_namespace('lightfield')

    @singleton
    @provider
    def provide_font(self) -> ImageFont:
        return ImageFont.truetype(io.BytesIO(pkgutil.get_data("lfcontrol", "fonts/pixelated.ttf")), 8)

    @singleton
    @provider
    def provide_pickledb(self, config: ConfigManager) -> pickledb.PickleDB:
        path = config('pickledb_file', default='/data/.lightfield_data.db')
        return pickledb.load(path, False)
