import configparser
import os

from ..environment import CliCanaryTestCase

COMMAND_NAME = 'config'


class CliConfigCommandTestCase(CliCanaryTestCase):
    def run_config_command(self, arguments=[], config_file=None,
                           expected_returncode=0):
        command = [COMMAND_NAME] + arguments
        if config_file:
            command = ['--config', config_file] + command

        return self.run_cli_command(
            command,
            expected_returncode=expected_returncode,
            )

    def assertConfigFileIs(self, file, expected):
        cp = configparser.ConfigParser()
        cp.read(file)

        actual = {}
        for section in cp.sections():
            section_value = {}

            for option, value in cp.items(section):
                section_value[option] = value

            actual[section] = section_value

        self.assertEqual(actual, expected)

    def test_config_non_existing_no_params(self):
        with self.prepared_environment() as dir:
            config_file = os.path.join(dir, 'config')
            self.run_config_command(config_file=config_file)

            self.assertConfigFileIs(config_file, {})

    def test_config_create_directory(self):
        with self.prepared_environment() as dir:
            config_file = os.path.join(dir, 'dir', 'config')
            self.run_config_command(
                ['--email', 'foo@example.org'],
                config_file=config_file)

            self.assertConfigFileIs(
                config_file,
                {'api': {'email': 'foo@example.org'}},
                )

    def test_config_non_existing_param_email(self):
        with self.prepared_environment() as dir:
            config_file = os.path.join(dir, 'config')
            self.run_config_command(
                ['--email', 'foo@example.org'],
                config_file=config_file)

            self.assertConfigFileIs(
                config_file,
                {'api': {'email': 'foo@example.org'}},
                )

    def test_config_existing_param_email(self):
        fixture = 'config-simple'
        with self.prepared_environment(fixture) as dir:
            config_file = os.path.join(dir, fixture, 'config')
            self.run_config_command(
                ['--email', 'foo@example.org'],
                config_file=config_file)

            self.assertConfigFileIs(
                config_file,
                {
                    'api': {
                        'email': 'foo@example.org',
                        'password': 'SECRET',
                        'quux': 'quuux'},
                    'foo': {'bar': 'quux'},
                },
                )

    def test_config_non_existing_param_password(self):
        with self.prepared_environment() as dir:
            config_file = os.path.join(dir, 'config')
            self.run_config_command(
                ['--password', 'secret'],
                config_file=config_file)

            self.assertConfigFileIs(
                config_file,
                {'api': {'password': 'secret'}},
                )

    def test_config_all_params(self):
        with self.prepared_environment() as dir:
            config_file = os.path.join(dir, 'config')
            self.run_config_command(
                ['--email', 'foo@example.org',
                 '--password', 'secret',
                 ],
                config_file=config_file)

            self.assertConfigFileIs(
                config_file,
                {'api': {
                        'email': 'foo@example.org',
                        'password': 'secret',
                        }},
                )

    def test_config_dump_blanking_no_params(self):
        fixture = 'config-passwords'
        with self.prepared_environment(fixture) as dir:
            config_file = os.path.join(dir, fixture, 'config')
            result = self.run_config_command(
                ['--dump'],
                config_file=config_file)

            self.assertEqual(result['stderr'], '')
            self.assertEqual(result['stdout'], '\n'.join([
                    '[api]',
                    'email = bar',
                    'password = <<BLANKED>>',
                    'secret = <<BLANKED>>',
                    '',
                    '[foo]',
                    'bar = quux',
                    'passcode = <<BLANKED>>',
                    '',
                    '[bar]',
                    'foo = quuux',
                    '',
                    '',
                    ]))

            self.assertConfigFileIs(
                config_file,
                {'api': {
                        'email': 'bar',
                        'password': 'i-will-not-tell',
                        'secret': 'give-up',
                        },
                 'foo': {
                        'bar': 'quux',
                        'passcode': 'no-chance',
                        },
                 'bar': {
                        'foo': 'quuux',
                        }},
                )

    def test_config_dump_blanking_while_setting_all(self):
        fixture = 'config-passwords'
        with self.prepared_environment(fixture) as dir:
            config_file = os.path.join(dir, fixture, 'config')
            result = self.run_config_command(
                ['--email', 'foo@example.org',
                 '--password', 'secret',
                 '--dump',
                 ],
                config_file=config_file)

            self.assertEqual(result['stderr'], '')
            self.assertEqual(result['stdout'], '\n'.join([
                    '[api]',
                    'email = foo@example.org',
                    'password = <<BLANKED>>',
                    'secret = <<BLANKED>>',
                    '',
                    '[foo]',
                    'bar = quux',
                    'passcode = <<BLANKED>>',
                    '',
                    '[bar]',
                    'foo = quuux',
                    '',
                    '',
                    ]))

            self.assertConfigFileIs(
                config_file,
                {'api': {
                        'email': 'foo@example.org',
                        'password': 'secret',
                        'secret': 'give-up',
                        },
                 'foo': {
                        'bar': 'quux',
                        'passcode': 'no-chance',
                        },
                 'bar': {
                        'foo': 'quuux',
                        }},
                )

    def test_config_dump_unblanked_no_params(self):
        fixture = 'config-passwords'
        with self.prepared_environment(fixture) as dir:
            config_file = os.path.join(dir, fixture, 'config')
            result = self.run_config_command(
                ['--dump-unblanked'],
                config_file=config_file)

            self.assertEqual(result['stderr'], '')
            self.assertEqual(result['stdout'], '\n'.join([
                    '[api]',
                    'email = bar',
                    'password = i-will-not-tell',
                    'secret = give-up',
                    '',
                    '[foo]',
                    'bar = quux',
                    'passcode = no-chance',
                    '',
                    '[bar]',
                    'foo = quuux',
                    '',
                    '',
                    ]))

            self.assertConfigFileIs(
                config_file,
                {'api': {
                        'email': 'bar',
                        'password': 'i-will-not-tell',
                        'secret': 'give-up',
                        },
                 'foo': {
                        'bar': 'quux',
                        'passcode': 'no-chance',
                        },
                 'bar': {
                        'foo': 'quuux',
                        }},
                )

    def test_config_dump_unblanked_while_setting_all(self):
        fixture = 'config-passwords'
        with self.prepared_environment(fixture) as dir:
            config_file = os.path.join(dir, fixture, 'config')
            result = self.run_config_command(
                ['--email', 'foo@example.org',
                 '--password', 'secret',
                 '--dump-unblanked',
                 ],
                config_file=config_file)

            self.assertEqual(result['stderr'], '')
            self.assertEqual(result['stdout'], '\n'.join([
                    '[api]',
                    'email = foo@example.org',
                    'password = secret',
                    'secret = give-up',
                    '',
                    '[foo]',
                    'bar = quux',
                    'passcode = no-chance',
                    '',
                    '[bar]',
                    'foo = quuux',
                    '',
                    '',
                    ]))

            self.assertConfigFileIs(
                config_file,
                {'api': {
                        'email': 'foo@example.org',
                        'password': 'secret',
                        'secret': 'give-up',
                        },
                 'foo': {
                        'bar': 'quux',
                        'passcode': 'no-chance',
                        },
                 'bar': {
                        'foo': 'quuux',
                        }},
                )
