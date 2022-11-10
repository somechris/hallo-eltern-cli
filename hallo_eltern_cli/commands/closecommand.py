# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from . import ApiCommand


class CloseCommand(ApiCommand):
    @classmethod
    def get_help(cls):
        return 'marks a message as closed'

    @classmethod
    def register_options(cls, parser):
        super(CloseCommand, cls).register_options(parser)

        parser.add_argument('id', help='The id of the message to close')

    def run(self):
        id = self._args.id
        child_code = self.get_child_code_for_message_id(id)
        self._api.close_message(id, child_code)
        print(f'Message {id} is now closed')
