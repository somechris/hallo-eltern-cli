#!/usr/bin/env python3

import argparse
import configparser
import json
import os
import requests
import socket
import subprocess

from datetime import datetime, timezone
from email.message import EmailMessage

CONFIG_DIR=os.path.join(os.path.expanduser('~'), '.config', 'hallo-eltern-app4email')
DEFAULT_CONFIG="""
[api]
base_url=https://hallo-api.klassenpinnwand.at/edugroup/api/v1
email=foo@example.org
password=bar

[email]
from=hallo-eltern-app@example.org
to=${email:from}
confirmed_subject_prefix=[confirmed]{{SPACE}}

[base]
user-agent=hallo-eltern-app4email/0.0.1
"""

def get_api_headers(config, user_id=None, auth_token=None):
    headers = {
        'user-agent': config.get('base', 'user-agent'),
    }

    if user_id is not None:
        headers['mogree-Access-Id'] = str(user_id)

    if auth_token is not None:
        headers['Cookie'] = f"mogree-Access-Token-Parent={auth_token}"

    return headers


def get_api_access_tokens(config):
    headers = get_api_headers(config)
    headers['mail'] = config.get('api', 'email')
    headers['password'] = config.get('api', 'password')

    response = requests.post(config.get('api', 'base_url') + '/account/login', headers=headers)
    result = response.json()['detailresponse']
    return (result['userid'], result['auth_token'])


def get_api_pinboards(config, user_id, auth_token):
    headers = get_api_headers(config, user_id, auth_token)

    response = requests.get(config.get('api', 'base_url') + '/pinboard', headers=headers)

    return response.json()['listresponse']


def get_api_messages(config, user_id, auth_token, pinboard, childcode):
    headers = {
        'user-agent': config.get('base', 'user-agent'),
        'Cookie': f"mogree-Access-Token-Parent={auth_token}",
        'mogree-Access-Id': str(user_id),
        }

    params = {
        'search': '',
        'closed': 'false',
        'pagingresults': '10',
        'pinboard': pinboard,
        'childcode': childcode,
        'time': int(get_datetime().timestamp())
    }

    response = requests.get(config.get('api', 'base_url') + '/messages', params=params, headers=headers)
    return response.json()['listresponse']


def get_data(config, data_file):
    data={'listresponse': []}
    if data_file:
        with open(data_file, 'r') as f:
            data = json.load(f)['listresponse']
    else:
        (user_id, auth_token) = get_api_access_tokens(config)
        pinboard_entries = get_api_pinboards(config, user_id, auth_token)
        data = []
        for entry in pinboard_entries:
            pinboard = entry['itemid']
            child_code = entry['code']
            messages = get_api_messages(config, user_id, auth_token, pinboard, child_code)
            data += messages
    return data


def get_message_id(message, config, confirmed=False):
    return f"<message-id-{message['itemid']}-{'confirmed' if confirmed else 'unconfirmed'}@{config.get('email', 'from').rsplit('@', 1)[1]}>"


def get_datetime():
    return datetime.now(timezone.utc)


def convert_message_to_email(message, config):
    now = get_datetime()
    confirmed = 'confirmed_by' in message

    email = EmailMessage()
    email['From'] = f"{message['sender']['title']} <{config.get('email', 'from')}>"
    email['To'] = f"{config.get('email', 'to')}"
    email['Subject'] = (config.get('email', 'confirmed_subject_prefix').replace('{{SPACE}}', ' ') if confirmed else '') + message['title'] 
    email['Date'] = datetime.fromisoformat(message['date'][0:22] + ':00')
    email['Received'] = f"from Hallo-Eltern-App with hallo-eltern-app4email by {socket.getfqdn()} for <{config.get('email', 'to')}>; {now}"
    email['Message-ID'] = get_message_id(message, config, confirmed=confirmed)
    email['User-Agent'] = config.get('base', 'user-agent')

    if confirmed:
        unconfirmed_message_id = get_message_id(message, config, confirmed=False)
        email['In-Reply-To'] = unconfirmed_message_id
        email['References'] = unconfirmed_message_id

    email['X-HalloElternApp-Sender-Id'] = message['sender']['itemid']
    email['X-HalloElternApp-Confirmation-Needed'] = str(message['confirmation'])
    email['X-HalloElternApp-Confirmed'] = 'True' if confirmed else 'False'
    email['X-HalloElternApp-Item-Id'] = message['itemid']

    email.set_content(message['message'])

    return email


def deliver_email_procmail(email):
            subprocess.run(["/usr/bin/procmail"],
                           input=str(email),
                           text=True,
                           check=True)


def deliver_email_stdout(email):
    print(email)


def deliver_email(email, mode):
    if mode == 'procmail':
        deliver_email_procmail(email)
    else:
        deliver_email_stdout(email)


def process_message(message, mode, config):
    email = convert_message_to_email(message, config)
    deliver_email(email, mode)


def process_data(data, mode, config):
    for message in data:
        process_message(message, mode, config)


def parse_config(config_file):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read_string(DEFAULT_CONFIG)
    if os.path.isfile(config_file):
        config.read(config_file)
    return config


def parse_arguments():
    parser = argparse.ArgumentParser(description='Turn messages from Hallo-Eltern-App into email')
    parser.add_argument('--mode', default='stdout', choices=['procmail', 'stdout'], help='where to pipe generated emails to')
    parser.add_argument('--config', default=os.path.join(CONFIG_DIR, 'config'), help='path to config file')
    parser.add_argument('--data-file', help='load message data from this file instead of querying the live API instance')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    config = parse_config(args.config)
    data = get_data(config, args.data_file)
    process_data(data, mode=args.mode, config=config)
