#!/usr/bin/env python3
# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import logging

from . import get_argument_parser, handle_parsed_default_args

from . import commands

logger = logging.getLogger(__name__)

COMMAND_CLASSES = [
    commands.ListCommand,
    commands.ShowCommand,
    commands.OpenCommand,
    commands.CloseCommand,
    commands.ConfigCommand,
    commands.TestCommand,
    ]
DEFAULT_COMMAND_CLASS = commands.ListCommand


def parse_arguments():
    parser = get_argument_parser(
        description='Simple CLI interface for Hallo-Eltern-App')

    subparsers = parser.add_subparsers(
        title='commands', description='available commands')
    for command_class in COMMAND_CLASSES:
        command_class.register_subparser(subparsers)

    args = parser.parse_args()

    return handle_parsed_default_args(args)


def run():
    (args, config) = parse_arguments()

    _class = args.command if 'command' in args else DEFAULT_COMMAND_CLASS
    command = _class(args, config)
    command.run()


if __name__ == '__main__':
    run()
