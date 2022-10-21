# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import unittest
import collections.abc
import json
import os
import shutil
import subprocess
import tempfile

FIXTURE_DIR = os.path.join('tests', 'fixtures')


class NotCleanedUpTemporaryDirectory(object):
    def __init__(self, prefix):
        self.name = tempfile.mkdtemp(prefix=prefix)

    def __enter__(self):
        return self.name

    def __exit__(self, exc, value, tb):
        pass


class BasicTestCase(unittest.TestCase):
    def get_fixture_file_name(self, name):
        return os.path.join(FIXTURE_DIR, name)

    def add_fixture(self, name, dir):
        src = self.get_fixture_file_name(name)
        dest = os.path.join(dir, name)
        if os.path.isdir(src):
            shutil.copytree(src, dest)
        else:
            shutil.copy(src, dest)

    def update_dict(self, target, source, merge_lists=False):
        for key, value in source.items():
            if isinstance(value, collections.abc.Mapping):
                repl = self.update_dict(target.get(key, {}), value)
                target[key] = repl
            elif merge_lists and isinstance(value, list) \
                    and isinstance(target.get(key, 0), list):
                target[key] += value
            else:
                target[key] = source[key]
        return target

    def prepared_environment(self, name=None, cleanup=True):
        temp_dir_cls = tempfile.TemporaryDirectory if cleanup \
            else NotCleanedUpTemporaryDirectory
        ctx = temp_dir_cls(prefix='hallo-eltern-cli-test-')

        dir = ctx.name

        if name:
            self.add_fixture(name, dir)

        return ctx

    def flatten(self, x):
        ret = []
        if isinstance(x, list):
            for element in x:
                ret += self.flatten(element)
        else:
            ret = [x]
        return ret

    def get_file_contents(self, file_name, text=True):
        flat_file_name = os.path.join(*self.flatten(file_name))
        with open(flat_file_name, 'r' + ('t' if text else 'b')) as file:
            contents = file.read()
        return contents

    def get_json_file_contents(self, file_name):
        return json.loads(self.get_file_contents(file_name))

    def assertFileJsonContents(self, file_name, expected):
        actual = self.get_json_file_contents(file_name)
        self.assertEqual(actual, expected)


class CanaryTestCase(BasicTestCase):
    def run_command(self, command, expected_returncode=0):
        process = subprocess.run(command,
                                 check=False,
                                 timeout=5,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)

        if process.returncode != expected_returncode:
            raise subprocess.CalledProcessError(
                process.returncode, process.args, process.stdout,
                process.stderr)

        return {
            'stdout': process.stdout,
            'stderr': process.stderr,
        }


class CliCanaryTestCase(CanaryTestCase):
    def run_cli_command(self, cli_arguments, expected_returncode=0):
        command = ['python3', '-m', 'hallo_eltern_cli.cli'] + cli_arguments

        return self.run_command(command,
                                expected_returncode=expected_returncode)
