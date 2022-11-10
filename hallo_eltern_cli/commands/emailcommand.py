# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from hallo_eltern_cli import MessageToEmailConverter

from . import ApiCommand


class EmailCommand(ApiCommand):
    def __init__(self, args, config):
        super(EmailCommand, self).__init__(args, config)

        self._message_converter = MessageToEmailConverter(
            self._config, self._api.get_authenticated_user(), self._api,
            forced_address=args.force_address)

    @classmethod
    def register_options(cls, parser):
        super(EmailCommand, cls).register_options(parser)

        parser.add_argument(
            '--force-address', default=None,
            help='Sets the To and From of generated emails to this value. '
            'Set this to your own email address to generate emails for '
            'submission to your email server.')
