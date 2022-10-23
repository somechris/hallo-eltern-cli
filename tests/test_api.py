# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from hallo_eltern_cli import Api

from .environment import BasicTestCase


class ApiTestCase(BasicTestCase):
    def create_api(self):
        config = {
            'user-agent': 'foo',
            }
        return Api(config)

    def test__extra_decode_data_None(self):
        api = self.create_api()
        actual = api._extra_decode(None)
        self.assertEqual(actual, None)

    def test__extra_decode_data_True(self):
        api = self.create_api()
        actual = api._extra_decode(True)
        self.assertEqual(actual, True)

    def test__extra_decode_data_False(self):
        api = self.create_api()
        actual = api._extra_decode(False)
        self.assertEqual(actual, False)

    def test__extra_decode_data_Number(self):
        api = self.create_api()
        actual = api._extra_decode(4711)
        self.assertEqual(actual, 4711)

    def test__extra_decode_data_string_plain(self):
        api = self.create_api()
        actual = api._extra_decode('foo')
        self.assertEqual(actual, 'foo')

    def test__extra_decode_data_string_umlaut(self):
        api = self.create_api()
        actual = api._extra_decode(r'für')
        self.assertEqual(actual, 'für')

    def test__extra_decode_data_string_umlaut_encoded(self):
        api = self.create_api()
        actual = api._extra_decode(r'f\u00FCr')
        self.assertEqual(actual, 'für')

    def test__extra_decode_data_string_CRs(self):
        api = self.create_api()
        actual = api._extra_decode('f\n\u00FC\\n\\u00FCr')
        self.assertEqual(actual, 'f\nü\nür')

    def test__extra_decode_data_list_plain(self):
        api = self.create_api()
        actual = api._extra_decode([1, 'foo', True])
        self.assertEqual(actual, [1, 'foo', True])

    def test__extra_decode_data_list_umlaut(self):
        api = self.create_api()
        actual = api._extra_decode([1, r'Wörter', True])
        self.assertEqual(actual, [1, 'Wörter', True])

    def test__extra_decode_data_list_umlaut_encoded(self):
        api = self.create_api()
        actual = api._extra_decode([1, r'W\u00f6rter', True])
        self.assertEqual(actual, [1, 'Wörter', True])

    def test__extra_decode_data_mapping_plain(self):
        api = self.create_api()
        actual = api._extra_decode({
                'foo': 1,
                'bar': 'baz',
                })
        self.assertEqual(actual, {
                'foo': 1,
                'bar': 'baz',
                })

    def test__extra_decode_data_mapping_umlaut(self):
        api = self.create_api()
        actual = api._extra_decode({
                'foo': 1,
                'bar': r'Österreich',
                })
        self.assertEqual(actual, {
                'foo': 1,
                'bar': 'Österreich',
                })

    def test__extra_decode_data_mapping_umlaut_encoded(self):
        api = self.create_api()
        actual = api._extra_decode({
                'foo': 1,
                'bar': r'\u00D6sterreich',
                })
        self.assertEqual(actual, {
                'foo': 1,
                'bar': 'Österreich',
                })

    def test__extra_decode_data_mapping_complex_plain(self):
        api = self.create_api()
        actual = api._extra_decode([{
                'foo': [1, False, 'quux'],
                'bar': {
                        'baz': ['quuux'],
                        'quux': 7,
                        }
                }, 'FOO'])
        self.assertEqual(actual, [{
                'foo': [1, False, 'quux'],
                'bar': {
                        'baz': ['quuux'],
                        'quux': 7,
                        }
                }, 'FOO'])

    def test__extra_decode_data_mapping_complex_umlaut(self):
        api = self.create_api()
        actual = api._extra_decode([{
                'foo': [1, False, 'groß'],
                'bar': {
                        'baz': [r'Lösung', r'Übung bräuchte'],
                        'quux': 7,
                        }
                }, 'Bäche'])
        self.assertEqual(actual, [{
                'foo': [1, False, 'groß'],
                'bar': {
                        'baz': ['Lösung', 'Übung bräuchte'],
                        'quux': 7,
                        }
                }, 'Bäche'])

    def test__extra_decode_data_mapping_complex_umlaut_encoded(self):
        api = self.create_api()
        actual = api._extra_decode([{
                'foo': [1, False, r'gro\u00DF'],
                'bar': {
                        'baz': [r'L\u00F6sung', r'\u00dcbung br\u00E4uchte'],
                        'quux': 7,
                        }
                }, r'B\u00e4che'])
        self.assertEqual(actual, [{
                'foo': [1, False, 'groß'],
                'bar': {
                        'baz': ['Lösung', 'Übung bräuchte'],
                        'quux': 7,
                        }
                }, 'Bäche'])
