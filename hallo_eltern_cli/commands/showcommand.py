# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from . import ApiCommand
from .utils import register_command_class
from hallo_eltern_cli import MessageToEmailConverter


class ShowCommand(ApiCommand):
    def __init__(self, args, config):
        super(ShowCommand, self).__init__(args, config)
        self._message_converter = MessageToEmailConverter(
            self._config, self._api.get_authenticated_user())

    @classmethod
    def register_subparser(cls, subparsers):
        parser = register_command_class(
            cls, subparsers, 'shows a message')
        parser.add_argument('id', help='The id of the message to show')

    def print_header(self, email, header):
        print(f'{header}: {email[header]}')

    def print_message(self, message, parent=None):
        email = self._message_converter.convert(message, parent=parent)
        self.print_header(email, 'From')
        self.print_header(email, 'To')
        self.print_header(email, 'Date')
        self.print_header(email, 'Subject')
        print()
        print(email.get_content())

    def run(self):
        id = self._args.id
        child_code = self.get_child_code_for_message_id(id)
        message = self._api.get_message(id, child_code)
        self.print_message(message)
        for answer in message['answers']:
            if answer['message']:
                print()
                self.print_separator()
                self.print_message(answer, message)
