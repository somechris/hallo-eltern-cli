# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from . import ApiCommand


class TestCommand(ApiCommand):
    @classmethod
    def get_help(cls):
        return 'tests the configured user againts the API'

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
