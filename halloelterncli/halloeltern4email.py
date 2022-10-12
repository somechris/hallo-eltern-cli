#!/usr/bin/env python3

import logging

import api
import common
import idstore
import messagetoemailconverter
import procmailmda
import stdoutmda

logger = logging.getLogger(__name__)


def parse_arguments():
    parser = common.get_argument_parser(
        description='Turn messages from Hallo-Eltern-App into email')
    parser.add_argument('--mode',
                        default='stdout',
                        choices=['procmail', 'stdout'],
                        help='where to pipe generated emails to')
    parser.add_argument('--data-file',
                        help='load message data from this file instead of '
                        'querying the live API instance')
    parser.add_argument('--process-all',
                        action='store_true',
                        help='process all (even already seen) messages')

    args = parser.parse_args()

    return common.handle_parsed_default_args(args)


class HalloElternApp4Email(object):
    def __init__(self, config):
        self._config = config
        self._api = api.Api(self._config)
        seen_ids_file = config.get('base', 'seen-ids-file')
        self._seen_ids_store = idstore.IdStore(seen_ids_file)

    def run(self, mda, process_all=False):
        converter = messagetoemailconverter.MessageToEmailConverter(
            self._config, self._api.get_authenticated_user())
        for pinboard in self._api.list_pinboards():
            pinboard_id = pinboard['itemid']
            child_code = pinboard['code']

            for message in self._api.list_messages(pinboard_id, child_code):
                confirmed_status = 'confirmed' if 'confirmed_by' in message \
                    else 'unconfirmed'
                id = f"{message['itemid']}-{confirmed_status}"
                if process_all or not self._seen_ids_store.has_been_seen(id):
                    email = converter.convert(message, {
                            'pinboard_id': pinboard_id,
                            'school_name': pinboard['school'],
                            'class_name': pinboard['subtitle'],
                            'child_name': pinboard['title'],
                            'child_code': child_code,
                            })
                    mda.deliver(email)
            self._seen_ids_store.persist()


if __name__ == '__main__':
    args = parse_arguments()
    config = common.get_config()

    if args.mode == 'procmail':
        mda = procmailmda.ProcmailMDA()
    elif args.mode == 'stdout':
        mda = stdoutmda.StdoutMDA()
    else:
        raise RuntimeError(f"Unknown mode '{args.mode}'")

    hea4e = HalloElternApp4Email(config)
    hea4e.run(mda, process_all=args.process_all)
