# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import json
import socket

from datetime import datetime, timezone
from email.message import EmailMessage


class MessageToEmailConverter(object):
    def __init__(self, config, authenticated_user, api=None,
                 forced_address=None):
        self._config = config
        self._message_id_domain = self._config.get('email', 'default-address')\
            .rsplit('@', 1)[1]
        self._authenticated_user = authenticated_user
        self._api = api
        self._forced_address = forced_address if forced_address is not None \
            else self._config.get('email', 'forced-address', fallback=None)

    def get_datetime(self):
        return datetime.now(timezone.utc)

    def get_message_id(self, message, confirmed=False):
        ret = f"<message-id-{message['itemid']}-"
        ret += 'confirmed' if confirmed else 'unconfirmed'
        ret += f"@{self._message_id_domain}>"
        return ret

    def _format_person(self, data):
        name = None
        address = None
        if data['itemid'] == self._authenticated_user['itemid']:
            first_name = self._authenticated_user['firstname']
            last_name = self._authenticated_user['lastname']
            name = f'{first_name} {last_name}'
            address = self._forced_address or self._authenticated_user['mail']
        else:
            name = data['title']
            address = self._forced_address or \
                self._config.get('email', 'default-address')
        return f'{name} <{address}>'

    def _build_to_header(self, message):
        receivers = ''
        if message['received']:
            receivers = [self._authenticated_user]
        else:
            if 'selected_receivers' in message:
                receivers = message['selected_receivers']
            else:
                receivers = [self._authenticated_user]

        return ', '.join([self._format_person(receiver)
                          for receiver in receivers])

    def _build_subject_header(self, message, confirmation_needed, confirmed,
                              parent):
        root_message = message if parent is None else parent
        ret = 'Re: ' if root_message != message else ''
        ret += root_message['title']
        if confirmed:
            prefix = self._config.get('email', 'confirmed-subject-prefix')
            prefix = prefix.replace('{{SPACE}}', ' ')
            ret = prefix + ret
        elif confirmation_needed:
            prefix = self._config.get(
                'email', 'confirmation-needed-subject-prefix')
            prefix = prefix.replace('{{SPACE}}', ' ')
            ret = prefix + ret
        return ret

    def _build_received_header(self):
        now = self.get_datetime()
        address = self._authenticated_user['mail']
        return ('from Hallo-Eltern-App with hallo-eltern-cli by '
                f"{socket.getfqdn()} for <{address}>; "
                f"{now}")

    def convert(self, message, extra_data={}, parent=None,
                embed_attachments=False):
        confirmation_needed = message['confirmation']
        confirmed = 'confirmed_by' in message
        email = EmailMessage()

        email['From'] = self._format_person(message['sender'])
        email['To'] = self._build_to_header(message)
        email['Subject'] = self._build_subject_header(
            message, confirmation_needed, confirmed, parent)
        email['Date'] = datetime.fromisoformat(message['date'][0:22] + ':00')
        email['Received'] = self._build_received_header()
        email['Message-ID'] = self.get_message_id(message, confirmed=confirmed)
        email['User-Agent'] = self._config.get('api', 'user-agent')

        replied_to_message = None
        if confirmed:
            replied_to_message = message
        elif parent:
            replied_to_message = parent

        if replied_to_message:
            replied_to_message_id = self.get_message_id(
                replied_to_message, confirmed=False)
            email['In-Reply-To'] = replied_to_message_id
            email['References'] = replied_to_message_id

        email['X-HalloElternApp-Sender-Id'] = message['sender']['itemid']
        email['X-HalloElternApp-Confirmation-Needed'] = \
            str(confirmation_needed)
        email['X-HalloElternApp-Confirmed'] = 'True' if confirmed else 'False'
        email['X-HalloElternApp-Item-Id'] = message['itemid']

        if 'child_name' in extra_data:
            email['X-HalloElternApp-Child-Name'] = extra_data['child_name']
        if 'class_name' in extra_data:
            email['X-HalloElternApp-Class-Name'] = extra_data['class_name']
        if 'school_name' in extra_data:
            email['X-HalloElternApp-School-Name'] = extra_data['school_name']

        content_json_string = message['message'].replace('\n', '\\n')
        message_content = json.loads('"' + content_json_string + '"')
        email.set_content(message_content)

        if 'link' in message and embed_attachments:
            filename = message.get('filename_client', 'attachment')
            ending = ('.' + filename).rsplit('.', 1)[1].lower()
            mime_type = 'application/octet-stream'
            if ending == 'jpg' or ending == 'jpeg':
                mime_type = 'image/jpeg'
            elif ending == 'pdf':
                mime_type = 'application/pdf'
            (mime_maintype, _, mime_subtype) = mime_type.partition('/')
            content = self._api.get_media_file(message['link'])
            email.add_attachment(content, maintype=mime_maintype,
                                 subtype=mime_subtype, filename=filename)
        return email
