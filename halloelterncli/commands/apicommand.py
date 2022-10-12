from . import BaseCommand
import api


class ApiCommand(BaseCommand):
    def __init__(self, args, config):
        super(ApiCommand, self).__init__(args, config)
        self._api = api.Api(self._config)
