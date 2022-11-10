# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from . import EmailCommand

from .utils import register_command_class


class StdoutCommand(EmailCommand):
    def __init__(self, args, config):
        super(StdoutCommand, self).__init__(args, config)

        self._process_all = args.process_all

        self._separator = args.separator
        self._processed_count = 0

    @classmethod
    def register_subparser(cls, subparsers):
        parser = register_command_class(
            cls, subparsers, 'dumps messages to stdout')

        parser.add_argument('--process-all',
                            action='store_true',
                            help='process all (even already seen) messages')

        parser.add_argument('--separator',
                            help='separator to print between messages')

    def process_email(self, email):
        if self._processed_count:
            print(self._separator)

        print(email)

        self._processed_count += 1
