#!/usr/bin/env python3
# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import logging

import halloelterncli
from halloelterncli import commands

logger = logging.getLogger(__name__)

COMMAND_CLASSES = [
    halloelterncli.commands.ListCommand,
    halloelterncli.commands.ShowCommand,
    halloelterncli.commands.OpenCommand,
    halloelterncli.commands.CloseCommand,
    halloelterncli.commands.ConfigCommand,
    halloelterncli.commands.TestCommand,
    ]
DEFAULT_COMMAND_CLASS = commands.ListCommand


def parse_arguments():
    parser = halloelterncli.get_argument_parser(
        description='Simple CLI interface for Hallo-Eltern-App')

    subparsers = parser.add_subparsers(
        title='commands', description='available commands')
    for command_class in COMMAND_CLASSES:
        command_class.register_subparser(subparsers)

    args = parser.parse_args()

    return halloelterncli.handle_parsed_default_args(args)


if __name__ == '__main__':
    (args, config) = parse_arguments()

    _class = args.command if 'command' in args else DEFAULT_COMMAND_CLASS
    command = _class(args, config)
    command.run()
