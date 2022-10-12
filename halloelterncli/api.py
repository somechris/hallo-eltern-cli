import requests
import logging

from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class Api(object):
    def __init__(self, config):
        self._config = config
        self._login_response = {}

    def _get_config(self, key):
        return self._config.get('api', key)

    def _compute_headers(self, custom_headers={}):
        ret = {
            'user-agent': self._get_config('user-agent'),
            }

        if 'userid' in self._login_response:
            ret['mogree-Access-Id'] = str(self._login_response['userid'])

        if 'auth_token' in self._login_response:
            auth_token = self._login_response['auth_token']
            ret['Cookie'] = f"mogree-Access-Token-Parent={auth_token}"

        if custom_headers:
            for k, v in custom_headers.items():
                ret[k] = v
        return ret

    def get_timestamp(self):
        return int(datetime.now(timezone.utc).timestamp())

    def _request(self, method, path, headers={}, parameters={},
                 authenticated=True):
        if authenticated and not self._login_response:
            self.authenticate()

        url = self._get_config('base_url') + path

        headers = self._compute_headers(custom_headers=headers)

        response_raw = method(url, headers=headers, params=parameters)

        logger.debug(f'api request to url: {url}\nheaders: {headers}\n'
                     f'parameters: {parameters}\n'
                     f'response status code: {response_raw.status_code}\n'
                     f'response:\n{response_raw.content.decode()}')

        response = response_raw.json()

        if response['statuscode'] != 200:
            raise RuntimeError(
                f"status code was {response['statuscode']} instead of 200")

        ret = None
        response_type = response['response_type']
        if response_type == 2:
            ret = response['listresponse']
        elif response_type == 3:
            ret = response['detailresponse']
        else:
            raise RuntimeError(f'Unknown response_type "{response_type}"')

        return ret

    def _get(self, path, headers={}, parameters={}, authenticated=True):
        return self._request(
            requests.get, path, headers=headers, parameters=parameters,
            authenticated=authenticated)

    def _post(self, path, headers={}, parameters={}, authenticated=True):
        return self._request(
            requests.post, path, headers=headers, parameters=parameters,
            authenticated=authenticated)

    def authenticate(self):
        self._login_response = {}
        headers = {
            'mail': self._get_config('email'),
            'password': self._get_config('password'),
            }

        self._login_response = self._post(
            '/account/login', headers=headers, authenticated=False)

    def get_authenticated_user(self):
        if not self._login_response:
            self.authenticate()
        return self._login_response['userdata']

    def list_pinboards(self):
        return self._get('/pinboard')

    def list_messages(self, pinboard, child_code):
        parameters = {
            'search': '',
            'closed': 'false',
            'pagingresults': '10',
            'pinboard': pinboard,
            'childcode': child_code,
            'time': self.get_timestamp(),
            }

        return self._get('/messages', parameters=parameters)

    def get_message(self, id, child_code):
        parameters = {
            'code': child_code,
            'time': self.get_timestamp(),
            }

        return self._get(f'/messages/{id}', parameters=parameters)

    def __str__(self):
        authenticated = bool(self._login_response)
        suffix = ''
        if authenticated:
            userdata = self._login_response['userdata']
            suffix = f", user: {userdata['mail']}, id:{userdata['id']}"
        return \
            f"halloelternappcli.Api(authenticated={authenticated}{suffix})"
