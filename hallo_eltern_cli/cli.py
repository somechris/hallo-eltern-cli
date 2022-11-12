#!/usr/bin/env python3
# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import argparse
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
    commands.HelpCommand,
    commands.MdaCommand,
    commands.StdoutCommand,
    commands.SmtpCommand,
    commands.VersionCommand,
    ]
DEFAULT_COMMAND_CLASS = commands.ListCommand
HELP_COMMAND_CLASS = commands.HelpCommand


def guess_command_name(cls):
    """Guess the inteded command name from the class name"""
    command_name = cls.__name__.lower()
    if command_name.endswith('command'):
        command_name = command_name[0:-7]
    return command_name


def parse_arguments():
    parser = get_argument_parser(
        description='Simple CLI interface for Hallo-Eltern-App')

    subparsers = parser.add_subparsers(
        title='commands', description='available commands')
    for cls in COMMAND_CLASSES:
        name = guess_command_name(cls)
        subparser = subparsers.add_parser(
            name, help=cls.get_help(),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser.set_defaults(command=cls)

        cls.register_options(subparser)

    args = parser.parse_args()

    # Since the `help` command needs the parser to produce the help message,
    # but does not have access to it, we short-circuit here, and show the help
    # page.
    if ('command' in args and args.command == HELP_COMMAND_CLASS):
        parser.print_help()

    return handle_parsed_default_args(args)


def run():
    (args, config) = parse_arguments()

    _class = args.command if 'command' in args else DEFAULT_COMMAND_CLASS
    if args.version:
        _class = commands.VersionCommand
    command = _class(args, config)
    command.run()


if __name__ == '__main__':
    run()
