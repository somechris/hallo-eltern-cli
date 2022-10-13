import configparser
import os

from halloelterncli import get_config

from . import BaseCommand
from .utils import register_command_class


class ConfigCommand(BaseCommand):
    @classmethod
    def register_subparser(cls, subparsers):
        parser = register_command_class(
            cls, subparsers, 'updates configuration')
        parser.add_argument(
            '--email', help='Sets the email to use for authentication')
        parser.add_argument(
            '--password', help='Sets the password to use for authentication. '
            'NOTE THAT THE PASSWORD WILL BE STORED AS PLAIN TEXT IN THE '
            'CONFIG FILE. DO NOT USE THIS UNLESS YOU USE EXTERNAL ENCRYPTION'
            'METHODS!')

    def _store_if_set(self, value, config, section, option):
        if value:
            # Setting a value of a non-existing section will fail, so
            # we try to opportunistically add the section beforehand.
            try:
                config.add_section(section)
            except configparser.DuplicateSectionError:
                # Section already exists. Nothing to do.
                pass
            except ValueError:
                # Trying to add default section. Nothing to do.
                pass
            config.set(section, option, value)

    def run(self):
        config_file = self._args.config
        config = get_config(config_file, load_defaults=False)

        self._store_if_set(self._args.password, config, 'api', 'password')
        self._store_if_set(self._args.email, config, 'api', 'email')

        config_file_dir = os.path.dirname(config_file)
        os.makedirs(config_file_dir, exist_ok=True)
        with open(config_file, 'w') as f:
            config.write(f)
