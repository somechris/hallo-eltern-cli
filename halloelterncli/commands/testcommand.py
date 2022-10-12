from . import ApiCommand
from .utils import register_command_class


class TestCommand(ApiCommand):
    @classmethod
    def register_subparser(cls, subparsers):
        register_command_class(
            cls, subparsers, 'tests the configured user againts the API')

    def run(self):
        response = self._api.authenticate()
        if response:
            userdata = response['userdata']
            firstname = userdata['firstname']
            lastname = userdata['lastname']
            mail = userdata['mail']
            print(f'Authenticated as {firstname} {lastname} (email: {mail})')
        else:
            raise RuntimeError('Authentication failed')