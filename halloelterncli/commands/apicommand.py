from . import BaseCommand
import api


class ApiCommand(BaseCommand):
    def __init__(self, args, config):
        super(ApiCommand, self).__init__(args, config)
        self._api = api.Api(self._config)

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

        if ret is None:
            raise RuntimeError(f'Failed to find child code for message {id}')

        return ret
