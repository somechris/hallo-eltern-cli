#!/usr/bin/env python3

import logging

import common
import commands

logger = logging.getLogger(__name__)

COMMAND_CLASSES = [
    commands.ListCommand,
    commands.ShowCommand,
    commands.TestCommand,
    ]
DEFAULT_COMMAND_CLASS = commands.ListCommand


def parse_arguments():
    parser = common.get_argument_parser(
        description='Simple CLI interface for Hallo-Eltern-App')

    subparsers = parser.add_subparsers(
        title='commands', description='available commands')
    for command_class in COMMAND_CLASSES:
        command_class.register_subparser(subparsers)

    args = parser.parse_args()

    return common.handle_parsed_default_args(args)


if __name__ == '__main__':
    (args, config) = parse_arguments()

    _class = args.command if 'command' in args else DEFAULT_COMMAND_CLASS
    command = _class(args, config)
    command.run()
