#!/usr/bin/env python3
# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import logging

import hallo_eltern_cli
from hallo_eltern_cli import commands

logger = logging.getLogger(__name__)

COMMAND_CLASSES = [
    hallo_eltern_cli.commands.ListCommand,
    hallo_eltern_cli.commands.ShowCommand,
    hallo_eltern_cli.commands.OpenCommand,
    hallo_eltern_cli.commands.CloseCommand,
    hallo_eltern_cli.commands.ConfigCommand,
    hallo_eltern_cli.commands.TestCommand,
    ]
DEFAULT_COMMAND_CLASS = commands.ListCommand


def parse_arguments():
    parser = hallo_eltern_cli.get_argument_parser(
        description='Simple CLI interface for Hallo-Eltern-App')

    subparsers = parser.add_subparsers(
        title='commands', description='available commands')
    for command_class in COMMAND_CLASSES:
        command_class.register_subparser(subparsers)

    args = parser.parse_args()

    return hallo_eltern_cli.handle_parsed_default_args(args)


if __name__ == '__main__':
    (args, config) = parse_arguments()

    _class = args.command if 'command' in args else DEFAULT_COMMAND_CLASS
    command = _class(args, config)
    command.run()
