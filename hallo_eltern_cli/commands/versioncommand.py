# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from . import BaseCommand, __version__


class VersionCommand(BaseCommand):
    @classmethod
    def get_help(cls):
        return 'prints the version number'

    def run(self):
        name = self.__module__.split('.')[0].replace('_', '-')
        version = __version__
        print(f'{name} {version}')
