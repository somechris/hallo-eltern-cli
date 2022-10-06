import socket

from datetime import datetime, timezone
from email.message import EmailMessage

class MessageToEmailConverter(object):
    def __init__(self, config):
        self._config = config

    def get_datetime(self):
        return datetime.now(timezone.utc)

    def get_message_id(self, message, config, confirmed=False):
        return f"<message-id-{message['itemid']}-{'confirmed' if confirmed else 'unconfirmed'}@{config.get('email', 'default-address').rsplit('@', 1)[1]}>"

    def convert(self, message, extra_data):
        now = self.get_datetime()
        confirmed = 'confirmed_by' in message
        authenticated_user = extra_data['logged_in_user']

        email = EmailMessage()
        if message['received']:
            from_header = f"{message['sender']['title']} <{self._config.get('email', 'default-address')}>"
            to_header = authenticated_user
        else:
            from_header = authenticated_user
            to_header = ', '.join([f"{receiver['title']} <{self._config.get('email', 'default-address')}>" for receiver in message['selected_receivers']])

        email['From'] = from_header
        email['To'] = to_header
        email['Subject'] = (self._config.get('email', 'confirmed-subject-prefix').replace('{{SPACE}}', ' ') if confirmed else '') + message['title'] 
        email['Date'] = datetime.fromisoformat(message['date'][0:22] + ':00')
        email['Received'] = f"from Hallo-Eltern-App with hallo-eltern-app4email by {socket.getfqdn()} for {authenticated_user.rsplit(' ', 1)[1]}; {now}"
        email['Message-ID'] = self.get_message_id(message, self._config, confirmed=confirmed)
        email['User-Agent'] = self._config.get('api', 'user-agent')

        if confirmed:
            unconfirmed_message_id = self.get_message_id(message, self._config, confirmed=False)
            email['In-Reply-To'] = unconfirmed_message_id
            email['References'] = unconfirmed_message_id

            email['X-HalloElternApp-Sender-Id'] = message['sender']['itemid']
            email['X-HalloElternApp-Confirmation-Needed'] = str(message['confirmation'])
            email['X-HalloElternApp-Confirmed'] = 'True' if confirmed else 'False'
            email['X-HalloElternApp-Item-Id'] = message['itemid']
        if 'child_name' in extra_data:
            email['X-HalloElternApp-Child-Name'] = extra_data['child_name']
        if 'class_name' in extra_data:
            email['X-HalloElternApp-Class-Name'] = extra_data['class_name']
        if 'school_name' in extra_data:
            email['X-HalloElternApp-School-Name'] = extra_data['school_name']

        email.set_content(message['message'])

        return email

