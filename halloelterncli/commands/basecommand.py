# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

class BaseCommand(object):
    def __init__(self, args, config):
        self._args = args
        self._config = config

    def print_separator(self):
        print('---------------------------------------------------')

    @classmethod
    def register_subparser(cls, subparsers):
        raise NotImplementedError(
            'Please implement this fuction in your subclass')

    def run(self):
        raise NotImplementedError(
            'Please implement this fuction in your subclass')
