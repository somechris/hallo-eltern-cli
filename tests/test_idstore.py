# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import os

from halloelterncli import IdStore

from .environment import CliCanaryTestCase


class IdStoreTestCase(CliCanaryTestCase):
    def test_non_existing_state_loading(self):
        with self.prepared_environment() as dir:
            state_file = os.path.join(dir, 'state.json')
            IdStore(state_file)

    def test_directory_creation_upon_persisting(self):
        with self.prepared_environment() as dir:
            state_file = os.path.join(dir, 'foo', 'state.json')
            idstore = IdStore(state_file)
            idstore.persist()

            self.assertFileJsonContents(state_file, {})

    def test_persisting_setting_non_existing(self):
        with self.prepared_environment('idstore-simple') as dir:
            state_file = os.path.join(dir, 'idstore-simple', 'state.json')
            idstore = IdStore(state_file)

            idstore['4711'] = '42'

            idstore.persist()

            self.assertFileJsonContents(state_file, {
                    'foo': 'bar',
                    'baz': 'quux',
                    '4711': '42'})

    def test_persisting_setting_existing(self):
        with self.prepared_environment('idstore-simple') as dir:
            state_file = os.path.join(dir, 'idstore-simple', 'state.json')
            idstore = IdStore(state_file)

            idstore['foo'] = 'quuux'

            idstore.persist()

            self.assertFileJsonContents(state_file, {
                    'foo': 'quuux',
                    'baz': 'quux'})

    def test_double_setting(self):
        with self.prepared_environment('idstore-simple') as dir:
            state_file = os.path.join(dir, 'idstore-simple', 'state.json')
            idstore = IdStore(state_file)

            idstore['foo'] = 'quuux'
            idstore['foo'] = 'baaar'

            idstore.persist()

            self.assertFileJsonContents(state_file, {
                    'foo': 'baaar',
                    'baz': 'quux'})

            self.assertIn('foo', idstore)

    def test_contains_true_loaded(self):
        with self.prepared_environment('idstore-simple') as dir:
            state_file = os.path.join(dir, 'idstore-simple', 'state.json')
            idstore = IdStore(state_file)

            self.assertIn('foo', idstore)

    def test_contains_true_set(self):
        with self.prepared_environment('idstore-simple') as dir:
            state_file = os.path.join(dir, 'idstore-simple', 'state.json')
            idstore = IdStore(state_file)
            idstore['4711'] = '42'

            self.assertIn('4711', idstore)

    def test_contains_false(self):
        with self.prepared_environment('idstore-simple') as dir:
            state_file = os.path.join(dir, 'idstore-simple', 'state.json')
            idstore = IdStore(state_file)

            self.assertNotIn('4711', idstore)
