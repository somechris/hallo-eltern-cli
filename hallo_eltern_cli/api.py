# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import collections.abc
import copy
import json
import os
import re
import requests
import logging

from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class Api(object):
    def __init__(self, config):
        self._config = config
        self._session = requests.Session()
        self._drop_state()
        self._session.headers.update({
                'user-agent': self._get_config('user-agent'),
                })

    def _get_config(self, key):
        return self._config.get('api', key)

    def get_timestamp(self):
        return int(datetime.now(timezone.utc).timestamp())

    def _drop_state(self):
        self._login_response = {}
        self._session.headers.update({
                'mogree-Access-Id': None
                })
        self._session.cookies.clear()

    def _raw_request(self, method, url, headers, parameters, binary):
        logger.debug(f'api request {method} to url: {url}\n'
                     f'headers: {headers}\n'
                     f'session.headers: {self._session.headers}\n'
                     f'session.cookies: {self._session.cookies.get_dict()}\n'
                     f'parameters: {parameters}')

        session = self._session
        if method == 'GET':
            requests_method = session.get
        elif method == 'POST':
            requests_method = session.post
        elif method == 'PUT':
            requests_method = session.put
        else:
            raise RuntimeError(f"Unknown method '{method}'")

        response = requests_method(url, headers=headers, params=parameters)
        content = response.content

        logger.debug(f'response status code: {response.status_code}\n'
                     f'response.request.headers: {response.request.headers}\n'
                     f'response.headers: {response.headers}\n'
                     'response:\n'
                     f"{'<<binary data>>' if binary else content.decode()}")

        return content

    def _cache_filled_raw_request(self, method, url, headers, parameters,
                                  binary):
        cache_dir = self._config.get('development', 'cache-dir')
        headers_clone = copy.deepcopy(headers)
        parameters_clone = copy.deepcopy(parameters)

        # We strip out the password to avoid leaking it as file name
        try:
            del headers_clone['password']
        except KeyError:
            pass

        # We strip out the current time to improve hit rates
        try:
            del parameters_clone['time']
        except KeyError:
            pass

        sanitize = re.compile(r'[^a-zA-Z0-9]+')
        cache_file = os.path.join(
            cache_dir,
            re.sub(sanitize, '-', method),
            re.sub(sanitize, '-', url),
            re.sub(sanitize, '-', str(headers_clone)),
            re.sub(sanitize, '-', str(parameters_clone)),
            )
        cache_file_dir = os.path.dirname(cache_file)

        content = None
        if os.path.isfile(cache_file):
            with open(cache_file, 'rb') as f:
                content = f.read()
            logger.debug(
                f'Using cached content from {cache_file}\n'
                f"{'<<binary data>>' if binary else content.decode()}")
        else:
            logger.debug(f'Cache miss for {cache_file}')
            content = self._raw_request(
                method, url, headers, parameters, binary)

            os.makedirs(cache_file_dir, exist_ok=True)
            with open(cache_file, 'wb') as f:
                f.write(content)

        return content

    def _extra_decode(self, data):
        if isinstance(data, collections.abc.Mapping):
            for key, value in data.items():
                data[key] = self._extra_decode(value)
        elif isinstance(data, list):
            data = [self._extra_decode(item) for item in data]
        elif isinstance(data, str):
            tmp = data.replace('\n', '\\n')
            data = json.loads('"' + tmp + '"')
        return data

    def _request(self, method, path, headers={}, parameters={},
                 authenticated=True, binary=False):
        if authenticated and not self._login_response:
            self.authenticate()

        base_url = self._get_config('base_url')
        if path.startswith('/'):
            url = base_url + path
        else:
            if not path.startswith(base_url):
                raise RuntimeError(
                    f'Path {path} starts with neither / nor {base_url}')
            url = path

        if self._config.getboolean('development', 'development-mode'):
            response_raw = self._cache_filled_raw_request(
                method, url, headers, parameters, binary)
        else:
            response_raw = self._raw_request(
                method, url, headers, parameters, binary)

        if binary:
            ret = response_raw
        else:
            response = json.loads(response_raw)

            # Sometimes (but not always), `title` and `message` fields are
            # double encoded. E.g.: Message 2811194 has neither `title` nor
            # `message` double encoded. But 2877226 has its `title` and
            # 2860389 its `message` double encoded.
            # We fail to find a good heuristics of when which fields get
            # double encoded. So we double decode all string values. This will
            # falsely double decode a few outliers, but should get double
            # encoding undone while not distorting too many other messages.
            response = self._extra_decode(response)

            if response['statuscode'] != 200:
                raise RuntimeError(
                    f"status code was {response['statuscode']} instead of 200")

            ret = None
            response_type = response['response_type']
            if response_type == 1:
                ret = None
            elif response_type == 2:
                ret = response['listresponse']
            elif response_type == 3:
                ret = response['detailresponse']
            else:
                raise RuntimeError(f'Unknown response_type "{response_type}"')

        return ret

    def _get(self, path, headers={}, parameters={}, authenticated=True,
             binary=False):
        return self._request(
            'GET', path, headers=headers, parameters=parameters,
            authenticated=authenticated, binary=binary)

    def _post(self, path, headers={}, parameters={}, authenticated=True,
              binary=False):
        return self._request(
            'POST', path, headers=headers, parameters=parameters,
            authenticated=authenticated, binary=binary)

    def _put(self, path, headers={}, parameters={}, authenticated=True,
             binary=False):
        return self._request(
            'PUT', path, headers=headers, parameters=parameters,
            authenticated=authenticated, binary=binary)

    def authenticate(self):
        self._drop_state()

        headers = {
            'mail': self._get_config('email'),
            'password': self._get_config('password'),
            }

        self._login_response = self._post(
            '/account/login', headers=headers, authenticated=False)

        self._session.headers.update({
                'mogree-Access-Id': str(self._login_response['userid']),
                })
        # While the session picks up the cookies automatically for us, the
        # relevant Cookie response header (on 2022-10-22) contains 'Path'
        # twice. E.g.:
        #   Set-Cookie: mogree-Access-Token-Parent=[...];Path=;Path=/;[...]
        # The requests library picks up only the first Path (which is empty)
        # and follows RFC 6265. Hence, the default-path (~ directory of the
        # request) is assumed. So it does not match follow-up requests and
        # would not get used.
        # So we have to patch the cookie, to make sure `/` (i.e.: the second
        # Path parameter) gets used a the cookie's path. This allows the
        # cookie to get used for the follow-up requests
        auth_token = self._login_response['auth_token']
        for cookie in self._session.cookies:
            if cookie.name == 'mogree-Access-Token-Parent' \
                    and cookie.value == auth_token:
                # We've found the cookie with correct name and value.
                # Now we can to patch it's path to apply for the whole site.
                cookie.path = '/'

        return self._login_response

    def get_authenticated_user(self):
        if not self._login_response:
            self.authenticate()
        return self._login_response['userdata']

    def list_pinboards(self):
        return self._get('/pinboard')

    def list_messages(self, pinboard, child_code):
        base_parameters = {
            'search': '',
            'pagingresults': '10',
            'pinboard': pinboard,
            'childcode': child_code,
            'time': self.get_timestamp(),
            }

        messages = []
        for closed in ['true', 'false']:
            parameters = copy.deepcopy(base_parameters)
            parameters['closed'] = closed
            messages += self._get('/messages', parameters=parameters)

        return messages

    def get_message(self, id, child_code):
        parameters = {
            'code': child_code,
            'time': self.get_timestamp(),
            }

        return self._get(f'/messages/{id}', parameters=parameters)

    def close_message(self, id, child_code):
        parameters = {
            'open': 'false',
            'code': child_code,
            }

        return self._put(f'/messages/{id}', parameters=parameters)

    def open_message(self, id, child_code):
        parameters = {
            'open': 'true',
            'code': child_code,
            }

        return self._put(f'/messages/{id}', parameters=parameters)

    def get_media_file(self, full_url):
        return self._get(full_url, binary=True)

    def __str__(self):
        authenticated = bool(self._login_response)
        suffix = ''
        if authenticated:
            userdata = self._login_response['userdata']
            suffix = f", user: {userdata['mail']}, id:{userdata['id']}"
        return \
            f"halloelternappcli.Api(authenticated={authenticated}{suffix})"
