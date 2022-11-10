# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import configparser
import os
import sys

from hallo_eltern_cli import get_config

from . import BaseCommand


class ConfigCommand(BaseCommand):
    @classmethod
    def get_help(cls):
        return 'updates configuration'

    @classmethod
    def register_options(cls, parser):
        super(ConfigCommand, cls).register_options(parser)

        parser.add_argument(
            '--dump', action='store_true',
            help='Prints the config to stdout. Passwords will get blanked.')
        parser.add_argument(
            '--dump-unblanked', action='store_true',
            help='Prints the config to stdout. '
            'BE CAREFUL! THIS ALSO PRINTS PASSWORDS!')
        parser.add_argument(
            '--email', help='Sets the email to use for authentication')
        parser.add_argument(
            '--password', help='Sets the password to use for authentication. '
            'NOTE THAT THE PASSWORD WILL BE STORED AS PLAIN TEXT IN THE '
            'CONFIG FILE. DO NOT USE THIS UNLESS YOU USE EXTERNAL ENCRYPTION'
            'METHODS!')
        parser.add_argument(
            '--force-address', help='Sets the To and From of generated emails '
            'to this value. Set this to your own email address to generate '
            'emails for submission to your email server.')

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

    def dump(self, config, blank=True):
        # On Python <3.7, copy.deepcopy fails for configparser objects.
        # So we deep copy through reparsing.
        clone = configparser.ConfigParser()
        clone.read_dict(config)
        config = clone

        if blank:
            for section in config.values():
                for option in section:
                    lower_option = option.lower()
                    if 'pass' in lower_option or 'secr' in lower_option:
                        # The option looks like it's a password, so we blank
                        # it.
                        section[option] = '<<BLANKED>>'

        config.write(sys.stdout)

    def run(self):
        config_file = self._args.config
        config = get_config(config_file, load_defaults=False)

        self._store_if_set(self._args.password, config, 'api', 'password')
        self._store_if_set(self._args.email, config, 'api', 'email')
        self._store_if_set(
            self._args.force_address, config, 'email', 'forced-address')

        if self._args.dump:
            self.dump(config, blank=True)

        if self._args.dump_unblanked:
            self.dump(config, blank=False)

        config_file_dir = os.path.dirname(config_file)
        os.makedirs(config_file_dir, exist_ok=True)
        with open(config_file, 'w') as f:
            config.write(f)
