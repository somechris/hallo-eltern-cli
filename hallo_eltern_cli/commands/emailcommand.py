# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from hallo_eltern_cli import MessageToEmailConverter

from . import ApiCommand


class EmailCommand(ApiCommand):
    def __init__(self, args, config):
        super(EmailCommand, self).__init__(args, config)

        self._message_converter = MessageToEmailConverter(
            self._config, self._api.get_authenticated_user(), self._api)
