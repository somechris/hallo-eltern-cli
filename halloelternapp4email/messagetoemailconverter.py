import socket

from datetime import datetime, timezone
from email.message import EmailMessage


class MessageToEmailConverter(object):
    def __init__(self, config, authenticated_user):
        self._config = config
        self._message_id_domain = self._config.get('email', 'default-address')\
            .rsplit('@', 1)[1]
        self._authenticated_user = authenticated_user

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
            address = self._authenticated_user['mail']
        else:
            name = data['title']
            address = self._config.get('email', 'default-address')
        return f'{name} <{address}>'

    def _build_to_header(self, message):
        receivers = ''
        if message['received']:
            receivers = [self._authenticated_user]
        else:
            receivers = message['selected_receivers']

        return ', '.join([self._format_person(receiver)
                          for receiver in receivers])

    def _build_subject_header(self, message, confirmed):
        ret = message['title']
        if confirmed:
            prefix = self._config.get('email', 'confirmed-subject-prefix')
            prefix = prefix.replace('{{SPACE}}', ' ')
            ret = prefix + ret
        return ret

    def _build_received_header(self):
        now = self.get_datetime()
        address = self._authenticated_user['mail']
        return ('from Hallo-Eltern-App with hallo-eltern-app4email by '
                f"{socket.getfqdn()} for <{address}>; "
                f"{now}")

    def convert(self, message, extra_data):
        confirmed = 'confirmed_by' in message

        email = EmailMessage()

        email['From'] = self._format_person(message['sender'])
        email['To'] = self._build_to_header(message)
        email['Subject'] = self._build_subject_header(message, confirmed)
        email['Date'] = datetime.fromisoformat(message['date'][0:22] + ':00')
        email['Received'] = self._build_received_header()
        email['Message-ID'] = self.get_message_id(message, confirmed=confirmed)
        email['User-Agent'] = self._config.get('api', 'user-agent')

        if confirmed:
            unconfirmed_message_id = self.get_message_id(
                message, confirmed=False)
            email['In-Reply-To'] = unconfirmed_message_id
            email['References'] = unconfirmed_message_id

            email['X-HalloElternApp-Sender-Id'] = message['sender']['itemid']
            email['X-HalloElternApp-Confirmation-Needed'] = \
                str(message['confirmation'])
            email['X-HalloElternApp-Confirmed'] = \
                'True' if confirmed else 'False'
            email['X-HalloElternApp-Item-Id'] = message['itemid']
        if 'child_name' in extra_data:
            email['X-HalloElternApp-Child-Name'] = extra_data['child_name']
        if 'class_name' in extra_data:
            email['X-HalloElternApp-Class-Name'] = extra_data['class_name']
        if 'school_name' in extra_data:
            email['X-HalloElternApp-School-Name'] = extra_data['school_name']

        email.set_content(message['message'])

        return email
