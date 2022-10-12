from . import ApiCommand
from .utils import register_command_class
from messagetoemailconverter import MessageToEmailConverter


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

    def get_child_code_for_message_id(self, id):
        ret = None
        for pinboard in self._api.list_pinboards():
            if ret is None:
                pinboard_id = pinboard['itemid']
                child_code = pinboard['code']

                for message in self._api.list_messages(
                        pinboard_id, child_code):
                    if message['itemid'] == id:
                        ret = child_code
        return ret

    def print_header(self, email, header):
        print(f'{header}: {email[header]}')

    def print_message(self, message):
        email = self._message_converter.convert(message, extra_data={})
        self.print_header(email, 'From')
        self.print_header(email, 'To')
        self.print_header(email, 'Date')
        self.print_header(email, 'Subject')
        print()
        print(email.get_content())

    def run(self):
        id = self._args.id
        child_code = self.get_child_code_for_message_id(id)
        if child_code is None:
            raise RuntimeError(f'Failed to find child code for message {id}')
        message = self._api.get_message(id, child_code)
        self.print_message(message)
