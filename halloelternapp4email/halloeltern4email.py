#!/usr/bin/env python3

import json
import socket
import subprocess

from datetime import datetime, timezone
from email.message import EmailMessage

DUMMY_DOMAIN='example.org'
DUMMY_LOCAL_PART='hallo-eltern-app'
DUMMY_EMAIL_ADDRESS=DUMMY_LOCAL_PART + '@' + DUMMY_DOMAIN

def get_data():
    with open('hea.json', 'r') as f:
        data = json.load(f)
    return data['listresponse']


def convert_message_to_email(message):
    now = datetime.now(timezone.utc)

    email = EmailMessage()
    email['From'] = f"{message['sender']['title']} <{DUMMY_EMAIL_ADDRESS}>"
    email['To'] = f"{DUMMY_EMAIL_ADDRESS}"
    email['Subject'] = message['title']
    email['Date'] = datetime.fromisoformat(message['date'][0:22] + ':00')
    email['Received'] = f' from Hallo-Eltern-App with hallo-eltern-app4email by {socket.getfqdn()} for <{DUMMY_EMAIL_ADDRESS}>; {now}'
    email['Message-ID'] = f"<message-id-{message['itemid']}-{'confirmed' if 'confirmed_by' in message else 'unconfirmed'}@{DUMMY_DOMAIN}"

    email['X-HalloElternApp-Sender-Id'] = message['sender']['itemid']
    email['X-HalloElternApp-Confirmation-Needed'] = str(message['confirmation'])
    email['X-HalloElternApp-Confirmed'] = 'True' if 'confirmed_by' in message else 'False'
    email['X-HalloElternApp-Item-Id'] = message['itemid']

    email.set_content(message['message'])

    return email


def deliver_email(email):
            subprocess.run(["/usr/bin/procmail"],
                           input=str(email),
                           text=True,
                           check=True)


def process_message(message):
    email = convert_message_to_email(message)
    deliver_email(email)


def process_data(data):
    for message in data:
        process_message(message)


if __name__ == '__main__':
    data = get_data()
    process_data(data)
