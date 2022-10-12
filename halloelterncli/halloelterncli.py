#!/usr/bin/env python3

import logging

import api
import common

logger = logging.getLogger(__name__)


def parse_arguments():
    parser = common.get_argument_parser(
        description='Simple CLI interface for Hallo-Eltern-App')

    args = parser.parse_args()

    return common.handle_parsed_default_args(args)


class ListMessages(object):
    def __init__(self, config):
        self._config = config
        self._api = api.Api(self._config)

    def print_separator(self):
        print('---------------------------------------------------')

    def print_pinboard_header(self, pinboard):
        id = pinboard['itemid']
        title = pinboard['title']
        subtitle = pinboard['subtitle']
        school = pinboard['school']
        url = pinboard['pinboard_link']
        print(f'Pinboard {title} ({subtitle})')
        self.print_separator()
        print(f'(id: {id}, URL: {url})')
        print(f'(school: {school})')
        print()

    def print_message_header(self):
        print('Flags |   Id    | Subject')
        self.print_separator()

    def print_message_footer(self):
        self.print_separator()
        print('^^^^')
        print('||||')
        print('|||+-- C means message is closed for me')
        print('||+--- C means message is closed')
        print('|+---- ! message needs your confirmation, C means confirmed')
        print('+----- U means message is unread')

    def print_message(self, message):
        id = message['itemid']
        subject = message['title']
        unread = message['unread']
        confirmation_needed = message['confirmation']
        confirmed = 'confirmed_by' in message
        closed = message['closed']
        my_close_status = message['my_close_status']

        flags = ''.join([
                'N' if unread else ' ',
                'C' if confirmed else ('!' if confirmation_needed else ' '),
                'C' if closed else ' ',
                'C' if my_close_status else ' ',
                ])
        print(f'{flags}  | {id} | {subject}')

    def run(self):
        for pinboard in self._api.list_pinboards():
            pinboard_id = pinboard['itemid']
            child_code = pinboard['code']

            self.print_pinboard_header(pinboard)

            self.print_message_header()
            for message in self._api.list_messages(pinboard_id, child_code):
                self.print_message(message)
            self.print_message_footer()


if __name__ == '__main__':
    args = parse_arguments()
    config = common.get_config()
    ListMessages(common.get_config()).run()
