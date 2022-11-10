# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from hallo_eltern_cli import IdStore

from . import EmailCommand


class EmailProcessorCommand(EmailCommand):
    def __init__(self, args, config):
        super(EmailProcessorCommand, self).__init__(args, config)

        seen_ids_file = config.get('base', 'seen-ids-file')
        self._seen_ids_store = IdStore(seen_ids_file)

        self._process_all = args.process_all

    @classmethod
    def register_options(cls, parser):
        super(EmailProcessorCommand, cls).register_options(parser)

        parser.add_argument('--process-all',
                            action='store_true',
                            help='process all (even already seen) messages')

    def _get_store_id_for_message(self, message):
        confirmed_status = 'confirmed' if 'confirmed_by' in message \
            else 'unconfirmed'
        return f"{message['itemid']}-{confirmed_status}"

    def _process_message(self, message, extra_data, parent=None):
        store_id = self._get_store_id_for_message(message)
        if self._process_all or store_id not in self._seen_ids_store:
            email = self._message_converter.convert(
                message, extra_data, parent, embed_attachments=True)

            self.process_email(email)

            if parent:
                message_title = f"Re: {parent['title']}"
            else:
                message_title = message['title']
            store_tag = f"{message['date']}/{message_title}"
            self._seen_ids_store[store_id] = store_tag

    def run(self):
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

                self._process_message(message, extra_data)
                for answer in message['answers']:
                    if answer['message']:
                        self._process_message(
                            answer, extra_data, parent=message)

        self._seen_ids_store.persist()

    def process_email(self, email):
        raise NotImplementedError(
            'Please implement this fuction in your subclass')
