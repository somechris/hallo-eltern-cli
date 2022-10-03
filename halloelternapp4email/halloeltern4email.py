#!/usr/bin/env python3

import argparse
import configparser
import json
import os
import socket
import subprocess

from datetime import datetime, timezone
from email.message import EmailMessage

__version__ = '0.0.1'

CONFIG_DIR=os.path.join(os.path.expanduser('~'), '.config', 'hallo-eltern-app4email')
DEFAULT_CONFIG="""
[email]
from=hallo-eltern-app@example.org
to=${email:from}
"""

def get_data():
    with open('hea.json', 'r') as f:
        data = json.load(f)
    return data['listresponse']


def convert_message_to_email(message, config):
    now = datetime.now(timezone.utc)

    email = EmailMessage()
    email['From'] = f"{message['sender']['title']} <{config.get('email', 'from')}>"
    email['To'] = f"{config.get('email', 'to')}"
    email['Subject'] = message['title']
    email['Date'] = datetime.fromisoformat(message['date'][0:22] + ':00')
    email['Received'] = f" from Hallo-Eltern-App with hallo-eltern-app4email by {socket.getfqdn()} for <{config.get('email', 'to')}>; {now}"
    email['Message-ID'] = f"<message-id-{message['itemid']}-{'confirmed' if 'confirmed_by' in message else 'unconfirmed'}@{config.get('email', 'from').rsplit('@', 1)[1]}"
    email['User-Agent'] = f"hallo-eltern-app4email/{__version__}"

    email['X-HalloElternApp-Sender-Id'] = message['sender']['itemid']
    email['X-HalloElternApp-Confirmation-Needed'] = str(message['confirmation'])
    email['X-HalloElternApp-Confirmed'] = 'True' if 'confirmed_by' in message else 'False'
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

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    config = parse_config(args.config)
    data = get_data()
    process_data(data, mode=args.mode, config=config)
