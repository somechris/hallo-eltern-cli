# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import argparse
import configparser
import logging
import os

from . import __version__

CONFIG_DIR = os.path.join(
    os.path.expanduser('~'), '.config', 'hallo-eltern-cli')
CACHE_DIR = os.path.join(
    os.path.expanduser('~'), '.cache', 'hallo-eltern-cli')
DEFAULT_CONFIG = """
[api]
email=foo@example.org
password=bar
base_url=https://hallo-api.klassenpinnwand.at/edugroup/api/v1
user-agent=hallo-eltern-cli/{{VERSION}}

[email]
default-address=do-not-reply@example.org
forced-address=
confirmation-needed-subject-prefix=[Confirmation needed]{{SPACE}}
confirmed-subject-prefix=[Confirmed]{{SPACE}}

[base]
seen-ids-file={{CONFIG_DIR}}/seen-ids.json

[development]
development-mode=False
cache-dir={{CACHE_DIR}}/api-development

[smtp]
host = localhost
port = 25
"""\
    .replace('{{CONFIG_DIR}}', CONFIG_DIR)\
    .replace('{{CACHE_DIR}}', CACHE_DIR)\
    .replace('{{VERSION}}', __version__)\



LOG_FORMAT = ('%(asctime)s.%(msecs)03d %(levelname)-5s [%(threadName)s] '
              '%(filename)s:%(lineno)d - %(message)s')
LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)


def get_config(config_file, load_defaults=True):
    interpolation = configparser.ExtendedInterpolation()
    config = configparser.ConfigParser(interpolation=interpolation)
    if load_defaults:
        config.read_string(DEFAULT_CONFIG)
    if os.path.isfile(config_file):
        config.read(config_file)
    return config


def get_argument_parser(description):
    parser = argparse.ArgumentParser(
        description='Turn messages from Hallo-Eltern-App into email',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config',
                        default=os.path.join(CONFIG_DIR, 'config'),
                        help='path to config file')
    parser.add_argument('--development-mode',
                        action='store_true',
                        help='Use development mode (caches api calls)')
    parser.add_argument('--verbose', '-v',
                        default=0,
                        action='count',
                        help='increase verbosity')
    parser.add_argument('--version',
                        action='store_true',
                        help='print the version and exit')
    return parser


def handle_parsed_default_args(args):
    config = get_config(args.config)
    if args.development_mode:
        config.set('development', 'development-mode', 'True')

    if args.verbose > 0:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug('Running in debug mode')

    return (args, config)
