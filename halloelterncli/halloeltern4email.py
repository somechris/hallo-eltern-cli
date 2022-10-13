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
        self._converter = messagetoemailconverter.MessageToEmailConverter(
            self._config, self._api.get_authenticated_user(), self._api)
        self._process_all = args.process_all

    def _get_store_id_for_message(self, message):
        confirmed_status = 'confirmed' if 'confirmed_by' in message \
            else 'unconfirmed'
        return f"{message['itemid']}-{confirmed_status}"

    def deliver(self, message, mda, extra_data, parent=None):
        store_id = self._get_store_id_for_message(message)
        if self._process_all or store_id not in self._seen_ids_store:
            email = self._converter.convert(message, extra_data, parent,
                                            embed_attachments=True)
            mda.deliver(email)

            if parent:
                message_title = f"Re: {parent['title']}"
            else:
                message_title = message['title']
            store_tag = f"{message['date']}/{message_title}"
            self._seen_ids_store[store_id] = store_tag

    def run(self, mda):
        for pinboard in self._api.list_pinboards():
            pinboard_id = pinboard['itemid']
            child_code = pinboard['code']

            extra_data = {
                'pinboard_id': pinboard_id,
                'school_name': pinboard['school'],
                'class_name': pinboard['subtitle'],
                'child_name': pinboard['title'],
                'child_code': child_code,

                }
            for abstract in self._api.list_messages(pinboard_id, child_code):
                id = abstract['itemid']
                message = self._api.get_message(id, child_code)

                self.deliver(message, mda, extra_data)
                for answer in message['answers']:
                    if answer['message']:
                        self.deliver(answer, mda, extra_data,
                                     parent=message)

        self._seen_ids_store.persist()


if __name__ == '__main__':
    (args, config) = parse_arguments()

    if args.mode == 'procmail':
        mda = procmailmda.ProcmailMDA()
    elif args.mode == 'stdout':
        mda = stdoutmda.StdoutMDA()
    else:
        raise RuntimeError(f"Unknown mode '{args.mode}'")

    hea4e = HalloElternApp4Email(config)
    hea4e.run(mda)
