# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from . import ApiCommand


class LoginCommand(ApiCommand):
    def __init__(self, args, config):
        super(LoginCommand, self).__init__(args, config)
        self._config = config
        self._curl = args.curl

    @classmethod
    def get_help(cls):
        return 'logs in and dumps the authentication headers'

    @classmethod
    def register_options(cls, parser):
        super(LoginCommand, cls).register_options(parser)

        parser.add_argument(
            '--curl', action='store_true',
            help='Output authentication headers in curl format')

    def run(self):
        response = self._api.authenticate()
        user_id = str(response['userid'])
        auth_token = str(response['auth_token'])

        if self._curl:
            url = self._config.get('api', 'base_url')
            print(f"curl {url}"
                  f" -H 'mogree-Access-Id: {user_id}'"
                  " -H 'Cookie: mogree-Access-Token-Parent="
                  f"{auth_token}'")
        else:
            print(f"mogree-Access-Id: {user_id}")
            print("mogree-Access-Token-Parent: "
                  f"mogree-Access-Id: {auth_token}")
