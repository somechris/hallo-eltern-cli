# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import smtplib

from . import EmailProcessorCommand


class SmtpCommand(EmailProcessorCommand):
    def __init__(self, args, config):
        super(SmtpCommand, self).__init__(args, config)

        self._host = self._resolve_setting(args.smtp_host, 'host')
        self._port = self._resolve_setting(args.smtp_port, 'port', 'int')
        self._tls = self._resolve_setting(args.tls, 'tls', 'boolean')
        self._starttls = self._resolve_setting(
            args.starttls, 'starttls', 'boolean')
        self._user = self._resolve_setting(args.smtp_user, 'user')
        self._password = self._resolve_setting(args.smtp_password, 'password')

    def _resolve_setting(self, arg, value, kind='string'):
        ret = None
        if arg is not None and (kind != 'boolean' or arg):
            ret = arg
        else:
            method = None
            if kind == 'string':
                method = self._config.get
            elif kind == 'int':
                method = self._config.getint
            elif kind == 'boolean':
                method = self._config.getboolean
            else:
                raise RuntimeError('Logic error')

            ret = method('smtp', value, fallback=None)

        return ret

    @classmethod
    def get_help(cls):
        return 'sends messages as emails'

    @classmethod
    def register_options(cls, parser):
        super(SmtpCommand, cls).register_options(parser)

        parser.add_argument(
            '--smtp-host', default=None,
            help='The smtp server to connect to. '
            'This overrides the smtp.host configuration setting.')

        parser.add_argument(
            '--smtp-port', default=None,
            help='The port to connect the smtp server at. '
            'This overrides the smtp.port configuration setting.')

        parser.add_argument(
            '--tls', action='store_true',
            help='Connect the smtp server through TLS. '
            'This overrides the smtp.tls configuration setting.')

        parser.add_argument(
            '--starttls', action='store_true',
            help='Connect the smtp server without TLS and promote to TLS. '
            'This overrides the smtp.starttls configuration setting.')

        parser.add_argument(
            '--smtp-user', default=None,
            help='The username to connect the smtp server with. '
            'This overrides the smtp.user configuration setting.')

        parser.add_argument(
            '--smtp-password', default=None,
            help='The password to connect the smtp server with. '
            'This overrides the smtp.password configuration setting.')

    def get_connection(self):
        constructor = smtplib.SMTP_SSL if self._tls else smtplib.SMTP
        server = constructor(host=self._host, port=self._port)
        if self._starttls:
            server.starttls()
        if self._user:
            server.login(self._user, self._password)

        return server

    def process_email(self, email):
        server = self.get_connection()

        server.sendmail(email['From'], email['To'], email.as_string())

        server.quit()
