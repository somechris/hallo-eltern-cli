# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import configparser

from hallo_eltern_cli import MessageToEmailConverter

from .environment import BasicTestCase


class MessageToEmailConverterTestCase(BasicTestCase):
    def convertMessage(self, message, extra_config={}, forced_address=None):
        config_dict = {
            'email': {
                'default-address': 'foo@example.org',
                'confirmation-needed-subject-prefix': 'CNSP',
                },
            'api': {
                'user-agent': 'TestUserAgent',
                }
            }
        config_dict = self.update_dict(config_dict, extra_config)
        config = configparser.ConfigParser()
        config.read_dict(config_dict)
        authenticated_user = {
            'itemid': '4711',
            'firstname': 'John',
            'lastname': 'Doe',
            'mail': 'john.doe@example.org',
            }
        api = None
        converter = MessageToEmailConverter(
            config, authenticated_user, api, forced_address=forced_address)
        converted = converter.convert(message)
        return converted

    def test_simple_received(self):
        message = {
            'confirmation': True,
            'sender': {
                'itemid': '4712',
                'title': 'Jane Doe',
                },
            'received': True,
            'title': 'Bar',
            'date': '2022-10-01T12:13:14+0100',
            'itemid': '23',
            'message': 'quux',
            }
        actual = self.convertMessage(message)
        self.assertEqual(actual['From'], 'Jane Doe <foo@example.org>')
        self.assertEqual(actual['To'], 'John Doe <john.doe@example.org>')
        self.assertEqual(actual['Subject'], 'CNSPBar')
        self.assertEqual(actual['Date'], 'Sat, 01 Oct 2022 12:13:14 +0100')
        self.assertEqual(actual['Message-ID'],
                         '<message-id-23-unconfirmed@example.org>')
        self.assertEqual(actual['User-Agent'], 'TestUserAgent')
        self.assertEqual(actual['X-HalloElternApp-Sender-Id'], '4712')
        self.assertEqual(actual['X-HalloElternApp-Confirmation-Needed'],
                         'True')
        self.assertEqual(actual['X-HalloElternApp-Confirmed'], 'False')
        self.assertEqual(actual['X-HalloElternApp-Item-Id'], '23')
        self.assertEqual(actual.get_content(), 'quux\n')

    def test_simple_sent_to_single(self):
        message = {
            'confirmation': True,
            'sender': {
                'itemid': '4711',
                },
            'selected_receivers': [{
                'itemid': '4712',
                'title': 'Jane Doe',
                }],
            'received': False,
            'title': 'Bar',
            'date': '2022-10-01T12:13:14+0100',
            'itemid': '23',
            'message': 'quux',
            }
        actual = self.convertMessage(message)
        self.assertEqual(actual['From'], 'John Doe <john.doe@example.org>')
        self.assertEqual(actual['To'], 'Jane Doe <foo@example.org>')
        self.assertEqual(actual['Subject'], 'CNSPBar')
        self.assertEqual(actual['Date'], 'Sat, 01 Oct 2022 12:13:14 +0100')
        self.assertEqual(actual['Message-ID'],
                         '<message-id-23-unconfirmed@example.org>')
        self.assertEqual(actual['User-Agent'], 'TestUserAgent')
        self.assertEqual(actual['X-HalloElternApp-Sender-Id'], '4711')
        self.assertEqual(actual['X-HalloElternApp-Confirmation-Needed'],
                         'True')
        self.assertEqual(actual['X-HalloElternApp-Confirmed'], 'False')
        self.assertEqual(actual['X-HalloElternApp-Item-Id'], '23')
        self.assertEqual(actual.get_content(), 'quux\n')

    def test_message_special_characters(self):
        message = {
            'confirmation': True,
            'sender': {
                'itemid': '4712',
                'title': 'Jane Doe',
                },
            'received': True,
            'title': 'Bar',
            'date': '2022-10-01T12:13:14+0100',
            'itemid': '23',
            'message': r'quux\nquuux\nf\u00FCr\nw\u00E4hrend',
            }
        actual = self.convertMessage(message)
        self.assertEqual(actual['From'], 'Jane Doe <foo@example.org>')
        self.assertEqual(actual['To'], 'John Doe <john.doe@example.org>')
        self.assertEqual(actual['Subject'], 'CNSPBar')
        self.assertEqual(actual['Date'], 'Sat, 01 Oct 2022 12:13:14 +0100')
        self.assertEqual(actual['Message-ID'],
                         '<message-id-23-unconfirmed@example.org>')
        self.assertEqual(actual['User-Agent'], 'TestUserAgent')
        self.assertEqual(actual['X-HalloElternApp-Sender-Id'], '4712')
        self.assertEqual(actual['X-HalloElternApp-Confirmation-Needed'],
                         'True')
        self.assertEqual(actual['X-HalloElternApp-Confirmed'], 'False')
        self.assertEqual(actual['X-HalloElternApp-Item-Id'], '23')
        self.assertEqual(actual.get_content(), 'quux\nquuux\nfür\nwährend\n')

    def test_forced_address(self):
        message = {
            'confirmation': True,
            'sender': {
                'itemid': '4712',
                'title': 'Jane Doe',
                },
            'received': True,
            'title': 'Bar',
            'date': '2022-10-01T12:13:14+0100',
            'itemid': '23',
            'message': 'quux',
            }
        actual = self.convertMessage(
            message, {'email': {'forced-address': 'BAR@EXAMPLE.ORG'}})
        self.assertEqual(actual['From'], 'Jane Doe <BAR@EXAMPLE.ORG>')
        self.assertEqual(actual['To'], 'John Doe <BAR@EXAMPLE.ORG>')
        self.assertEqual(actual['Subject'], 'CNSPBar')
        self.assertEqual(actual['Date'], 'Sat, 01 Oct 2022 12:13:14 +0100')
        self.assertEqual(actual['Message-ID'],
                         '<message-id-23-unconfirmed@example.org>')
        self.assertEqual(actual['User-Agent'], 'TestUserAgent')
        self.assertEqual(actual['X-HalloElternApp-Sender-Id'], '4712')
        self.assertEqual(actual['X-HalloElternApp-Confirmation-Needed'],
                         'True')
        self.assertEqual(actual['X-HalloElternApp-Confirmed'], 'False')
        self.assertEqual(actual['X-HalloElternApp-Item-Id'], '23')
        self.assertEqual(actual.get_content(), 'quux\n')

    def test_forced_address_config_set_empty_overruled(self):
        message = {
            'confirmation': True,
            'sender': {
                'itemid': '4712',
                'title': 'Jane Doe',
                },
            'received': True,
            'title': 'Bar',
            'date': '2022-10-01T12:13:14+0100',
            'itemid': '23',
            'message': 'quux',
            }
        actual = self.convertMessage(
            message, {'email': {'forced-address': 'BAR@EXAMPLE.ORG'}},
            forced_address='')
        self.assertEqual(actual['From'], 'Jane Doe <foo@example.org>')
        self.assertEqual(actual['To'], 'John Doe <john.doe@example.org>')
        self.assertEqual(actual['Subject'], 'CNSPBar')
        self.assertEqual(actual['Date'], 'Sat, 01 Oct 2022 12:13:14 +0100')
        self.assertEqual(actual['Message-ID'],
                         '<message-id-23-unconfirmed@example.org>')
        self.assertEqual(actual['User-Agent'], 'TestUserAgent')
        self.assertEqual(actual['X-HalloElternApp-Sender-Id'], '4712')
        self.assertEqual(actual['X-HalloElternApp-Confirmation-Needed'],
                         'True')
        self.assertEqual(actual['X-HalloElternApp-Confirmed'], 'False')
        self.assertEqual(actual['X-HalloElternApp-Item-Id'], '23')
        self.assertEqual(actual.get_content(), 'quux\n')

    def test_forced_address_config_set_overruled(self):
        message = {
            'confirmation': True,
            'sender': {
                'itemid': '4712',
                'title': 'Jane Doe',
                },
            'received': True,
            'title': 'Bar',
            'date': '2022-10-01T12:13:14+0100',
            'itemid': '23',
            'message': 'quux',
            }
        actual = self.convertMessage(
            message, {'email': {'forced-address': 'BAR@EXAMPLE.ORG'}},
            forced_address='BAZ@EXAMPLE.ORG')
        self.assertEqual(actual['From'], 'Jane Doe <BAZ@EXAMPLE.ORG>')
        self.assertEqual(actual['To'], 'John Doe <BAZ@EXAMPLE.ORG>')
        self.assertEqual(actual['Subject'], 'CNSPBar')
        self.assertEqual(actual['Date'], 'Sat, 01 Oct 2022 12:13:14 +0100')
        self.assertEqual(actual['Message-ID'],
                         '<message-id-23-unconfirmed@example.org>')
        self.assertEqual(actual['User-Agent'], 'TestUserAgent')
        self.assertEqual(actual['X-HalloElternApp-Sender-Id'], '4712')
        self.assertEqual(actual['X-HalloElternApp-Confirmation-Needed'],
                         'True')
        self.assertEqual(actual['X-HalloElternApp-Confirmed'], 'False')
        self.assertEqual(actual['X-HalloElternApp-Item-Id'], '23')
        self.assertEqual(actual.get_content(), 'quux\n')

    def test_forced_address_config_unset_overruled(self):
        message = {
            'confirmation': True,
            'sender': {
                'itemid': '4712',
                'title': 'Jane Doe',
                },
            'received': True,
            'title': 'Bar',
            'date': '2022-10-01T12:13:14+0100',
            'itemid': '23',
            'message': 'quux',
            }
        actual = self.convertMessage(message, forced_address='BAZ@EXAMPLE.ORG')
        self.assertEqual(actual['From'], 'Jane Doe <BAZ@EXAMPLE.ORG>')
        self.assertEqual(actual['To'], 'John Doe <BAZ@EXAMPLE.ORG>')
        self.assertEqual(actual['Subject'], 'CNSPBar')
        self.assertEqual(actual['Date'], 'Sat, 01 Oct 2022 12:13:14 +0100')
        self.assertEqual(actual['Message-ID'],
                         '<message-id-23-unconfirmed@example.org>')
        self.assertEqual(actual['User-Agent'], 'TestUserAgent')
        self.assertEqual(actual['X-HalloElternApp-Sender-Id'], '4712')
        self.assertEqual(actual['X-HalloElternApp-Confirmation-Needed'],
                         'True')
        self.assertEqual(actual['X-HalloElternApp-Confirmed'], 'False')
        self.assertEqual(actual['X-HalloElternApp-Item-Id'], '23')
        self.assertEqual(actual.get_content(), 'quux\n')
