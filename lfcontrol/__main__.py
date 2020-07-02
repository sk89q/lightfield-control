import argparse
import logging

from injector import Injector

from lfcontrol.engine import ControlEngine
from lfcontrol.lightfield import LightField
from lfcontrol.module import ControlModule


def configure_wifi_ap(injector, args):
    lightfield = injector.get(LightField)
    lightfield.configure_wifi_ap(args.ssid, args.password)


def configure_wifi_client(injector, args):
    lightfield = injector.get(LightField)
    lightfield.configure_wifi_client(args.ssid, args.password)


def run(injector, args):
    engine = injector.get(ControlEngine)
    engine.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action='store_true', default=False)

    subparsers = parser.add_subparsers()

    subparser = subparsers.add_parser('configure-wifi-ap')
    subparser.add_argument('ssid')
    subparser.add_argument('password')
    subparser.set_defaults(func=configure_wifi_ap)

    subparser = subparsers.add_parser('configure-wifi-client')
    subparser.add_argument('ssid')
    subparser.add_argument('password')
    subparser.set_defaults(func=configure_wifi_client)

    subparser = subparsers.add_parser('run')
    subparser.set_defaults(func=run)

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s (%(levelname)s) [%(name)s] %(message)s",
                        datefmt="%H:%M:%S")

    injector = Injector([
        ControlModule(),
    ])
    lightfield = injector.get(LightField)
    logging.info(f"LightField URL: {lightfield.url}")
    args.func(injector, args)
