from . import ApiCommand
from .utils import register_command_class
from halloelterncli import MessageToEmailConverter


class OpenCommand(ApiCommand):
    def __init__(self, args, config):
        super(OpenCommand, self).__init__(args, config)
        self._message_converter = MessageToEmailConverter(
            self._config, self._api.get_authenticated_user())

    @classmethod
    def register_subparser(cls, subparsers):
        parser = register_command_class(
            cls, subparsers, 'closes a message')

        parser.add_argument('id', help='The id of the message to open')

    def run(self):
        id = self._args.id
        child_code = self.get_child_code_for_message_id(id)
        self._api.open_message(id, child_code)
        print(f'Message {id} is now open')
