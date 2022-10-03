#!/usr/bin/env python3

import json
import email.utils

from datetime import datetime
from email.message import EmailMessage


def get_data():
    with open('hea.json', 'r') as f:
        data = json.load(f)
    return data['listresponse']


def convert_message_to_email(message):
    email = EmailMessage()
    email['From'] = message['sender']['title']
    email['Subject'] = message['title']
    email['Date'] = datetime.fromisoformat(message['date'][0:22] + ':00')

    email['X-HalloElternApp-Sender-Id'] = message['sender']['itemid']
    email['X-HalloElternApp-Confirmation-Needed'] = str(message['confirmation'])
    email['X-HalloElternApp-Confirmed'] = 'True' if 'confirmed_by' in message else 'False'
    email['X-HalloElternApp-Item-Id'] = message['itemid']

    email.set_content(message['message'])

    return email


def process_message(message):
    email = convert_message_to_email(message)
    print(email)


def process_data(data):
    for message in data:
        process_message(message)


if __name__ == '__main__':
    data = get_data()
    process_data(data)
