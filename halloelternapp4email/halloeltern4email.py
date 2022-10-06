#!/usr/bin/env python3

import argparse
import configparser
import os

import api
import idstore
import messagetoemailconverter
import procmailmda
import stdoutmda

CONFIG_DIR=os.path.join(os.path.expanduser('~'), '.config', 'hallo-eltern-app4email')
SEEN_IDS={}
DEFAULT_CONFIG="""
[api]
email=foo@example.org
password=bar
base_url=https://hallo-api.klassenpinnwand.at/edugroup/api/v1
user-agent=hallo-eltern-app4email/0.0.1

[email]
default-address=do-not-reply@example.org
confirmed-subject-prefix=[confirmed]{{SPACE}}

[base]
seen-ids-file={{CONFIG_DIR}}/seen-ids.json
""".replace('{{CONFIG_DIR}}', CONFIG_DIR)



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
    parser.add_argument('--process-all', action='store_true', help='process all (even already seen) messages')

    return parser.parse_args()

class HalloElternApp4Email(object):
    def __init__(self, config):
        self._config = config
        self._api = api.Api(self._config)
        self._seen_ids_store = idstore.IdStore(config.get('base', 'seen-ids-file'))

    def run(self, mda, process_all=False):
        converter = messagetoemailconverter.MessageToEmailConverter(self._config)
        for pinboard in self._api.list_pinboards():
            pinboard_id=pinboard['itemid']
            child_code = pinboard['code']

            for message in self._api.list_messages(pinboard_id, child_code):
                id = f"{message['itemid']}-{'confirmed' if 'confirmed_by' in message else 'unconfirmed'}"
                if process_all or not self._seen_ids_store.has_been_seen(id):
                    email = converter.convert(message, {
                            'pinboard_id': pinboard_id,
                            'school_name': pinboard['school'],
                            'class_name': pinboard['subtitle'],
                            'child_name': pinboard['title'],
                            'child_code': child_code,
                            'logged_in_user': self._api.get_authenticated_user(),
                            })
                    mda.deliver(email)
            self._seen_ids_store.persist()

if __name__ == '__main__':
    args = parse_arguments()
    config = parse_config(args.config)

    if args.mode == 'procmail':
        mda = procmailmda.ProcmailMDA()
    elif args.mode == 'stdout':
        mda = stdoutmda.StdoutMDA()
    else:
        raise RuntimeError(f"Unknown mode '{args.mode}'")

    hea4e = HalloElternApp4Email(config)
    hea4e.run(mda, process_all=args.process_all)
