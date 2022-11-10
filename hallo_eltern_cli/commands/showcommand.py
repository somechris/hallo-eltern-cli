# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from . import EmailCommand


class ShowCommand(EmailCommand):
    @classmethod
    def get_help(cls):
        return 'shows a message'

    @classmethod
    def register_options(cls, parser):
        super(ShowCommand, cls).register_options(parser)

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
