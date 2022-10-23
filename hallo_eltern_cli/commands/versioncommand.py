# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from . import BaseCommand, __version__
from .utils import register_command_class


class VersionCommand(BaseCommand):
    @classmethod
    def register_subparser(cls, subparsers):
        register_command_class(
            cls, subparsers, 'prints the version number')

    def run(self):
        name = self.__module__.split('.')[0].replace('_', '-')
        version = __version__
        print(f'{name} {version}')
