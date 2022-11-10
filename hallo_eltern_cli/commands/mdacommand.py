# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import subprocess

from . import EmailCommand


class MdaCommand(EmailCommand):
    def __init__(self, args, config):
        super(MdaCommand, self).__init__(args, config)

        self._process_all = args.process_all

        self._mda_command = args.mda_command

    @classmethod
    def get_help(cls):
        return 'feeds messages into a message delivery agent (procmail, ' + \
            'maildrop, ...)'

    @classmethod
    def register_options(cls, parser):
        super(MdaCommand, cls).register_options(parser)

        parser.add_argument('--process-all',
                            action='store_true',
                            help='process all (even already seen) messages')

        parser.add_argument('--mda-command',
                            default='/usr/bin/procmail',
                            help='The command to start the MDA with')

    def process_email(self, email):
        subprocess.run([self._mda_command],
                       input=str(email),
                       text=True,
                       check=True)
