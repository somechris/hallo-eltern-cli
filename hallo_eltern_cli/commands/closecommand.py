# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from . import ApiCommand
from .utils import register_command_class


class CloseCommand(ApiCommand):
    @classmethod
    def register_subparser(cls, subparsers):
        parser = register_command_class(
            cls, subparsers, 'marks a message as closed')

        parser.add_argument('id', help='The id of the message to show')

    def run(self):
        id = self._args.id
        child_code = self.get_child_code_for_message_id(id)
        self._api.close_message(id, child_code)
        print(f'Message {id} is now closed')
