# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch, Mock

from hallo_eltern_cli.commands import ApiCommand
from ..environment import CanaryTestCase


class ApiCommandTestCase(CanaryTestCase):
    @patch('hallo_eltern_cli.Api')
    def create_command(self, Api):
        args = Mock()
        config = Mock()
        api = Mock()
        Api.return_value = api
        return (ApiCommand(args, config), api, args, config)

    def test_api_creation(self):
        (command, api, _, _) = self.create_command()
        self.assertEqual(command._api, api)

    def test_get_child_code_for_message_no_pinboards(self):
        (command, api, _, _) = self.create_command()
        api.list_pinboards.return_value = []

        with self.assertRaises(RuntimeError) as context:
            command.get_child_code_for_message_id(42)

        message = str(context.exception)
        self.assertIn('ailed', message)
        self.assertIn(' 42', message)

    def test_get_child_code_for_message_no_matching(self):
        (command, api, _, _) = self.create_command()
        api.list_pinboards.return_value = [
                {'itemid': 'pinFoo', 'code': 'codeFoo'},
                {'itemid': 'pinBar', 'code': 'codeBar'},
                ]

        def list_messages(id, code):
            if id == 'pinFoo' and code == 'codeFoo':
                return []
            elif id == 'pinBar' and code == 'codeBar':
                return [{'itemid': 4711}]
            else:
                self.fail(f'Unexpected list_message call ({id}, {code})')

        api.list_messages.side_effect = list_messages

        with self.assertRaises(RuntimeError) as context:
            command.get_child_code_for_message_id(42)

        message = str(context.exception)
        self.assertIn('ailed', message)
        self.assertIn(' 42', message)

    def test_get_child_code_for_message_match(self):
        (command, api, _, _) = self.create_command()
        api.list_pinboards.return_value = [
                {'itemid': 'pinFoo', 'code': 'codeFoo'},
                {'itemid': 'pinBar', 'code': 'codeBar'},
                {'itemid': 'pinBaz', 'code': 'codeBaz'},
                ]

        def list_messages(id, code):
            if id == 'pinFoo' and code == 'codeFoo':
                return [{'itemid': 23}, {'itemid': 14}]
            elif id == 'pinBar' and code == 'codeBar':
                return [{'itemid': 4711}, {'itemid': 42}, {'itemid': 19}]
            else:
                self.fail(f'Unexpected list_message call ({id}, {code})')

        api.list_messages.side_effect = list_messages

        actual = command.get_child_code_for_message_id(42)
        self.assertEqual(actual, 'codeBar')
