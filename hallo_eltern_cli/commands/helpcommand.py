# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from . import BaseCommand


class HelpCommand(BaseCommand):
    @classmethod
    def get_help(cls):
        return 'prints this help page'

    def run(self):
        # The printing of the message happens during argument parsing
        # in `cli.py`.
        pass
