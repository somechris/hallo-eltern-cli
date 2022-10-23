# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from ..environment import CliCanaryTestCase


class CliConfigCommandTestCase(CliCanaryTestCase):
    def test_version(self):
        result = self.run_cli_command(['version'])
        self.assertEmptyString(result['stderr'])
        stdout_parts = result['stdout'].split()
        self.assertEqual(stdout_parts[0], 'hallo-eltern-cli')
        self.assertRegex(stdout_parts[1],
                         r'^[0-9]+\.[0-9]+\.[0-9]+(-alpha\.[0-9]+)?$')
