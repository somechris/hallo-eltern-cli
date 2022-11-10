# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from . import EmailProcessorCommand


class StdoutCommand(EmailProcessorCommand):
    def __init__(self, args, config):
        super(StdoutCommand, self).__init__(args, config)

        self._separator = args.separator
        self._processed_count = 0

    @classmethod
    def get_help(cls):
        return 'dumps messages to stdout'

    @classmethod
    def register_options(cls, parser):
        super(StdoutCommand, cls).register_options(parser)

        parser.add_argument('--separator',
                            help='separator to print between messages')

    def process_email(self, email):
        if self._processed_count:
            print(self._separator)

        print(email)

        self._processed_count += 1
