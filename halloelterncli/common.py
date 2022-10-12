import argparse
import configparser
import logging
import os

CONFIG_DIR = os.path.join(
    os.path.expanduser('~'), '.config', 'hallo-eltern-cli')
CONFIG_FILE = None
DEFAULT_CONFIG = """
[api]
email=foo@example.org
password=bar
base_url=https://hallo-api.klassenpinnwand.at/edugroup/api/v1
user-agent=hallo-eltern-cli/0.0.1

[email]
default-address=do-not-reply@example.org
confirmed-subject-prefix=[confirmed]{{SPACE}}

[base]
seen-ids-file={{CONFIG_DIR}}/seen-ids.json
""".replace('{{CONFIG_DIR}}', CONFIG_DIR)


LOG_FORMAT = ('%(asctime)s.%(msecs)03d %(levelname)-5s [%(threadName)s] '
              '%(filename)s:%(lineno)d - %(message)s')
LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)


def get_config(config_file=None):
    if config_file is None:
        config_file = CONFIG_FILE
    interpolation = configparser.ExtendedInterpolation()
    config = configparser.ConfigParser(interpolation=interpolation)
    config.read_string(DEFAULT_CONFIG)
    if os.path.isfile(config_file):
        config.read(config_file)
    return config


def get_argument_parser(description):
    parser = argparse.ArgumentParser(
        description='Turn messages from Hallo-Eltern-App into email')
    parser.add_argument('--config',
                        default=os.path.join(CONFIG_DIR, 'config'),
                        help='path to config file')
    parser.add_argument('--verbose', '-v',
                        default=0,
                        action='count',
                        help='increase verbosity')
    return parser


def handle_parsed_default_args(args):
    global CONFIG_FILE
    CONFIG_FILE = args.config

    if args.verbose > 0:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug('Running in debug mode')

    return args