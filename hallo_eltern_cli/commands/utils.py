# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import argparse


def guess_command_name(cls):
    """Guess the inteded command name from the class name"""
    command_name = cls.__name__.lower()
    if command_name.endswith('command'):
        command_name = command_name[0:-7]
    return command_name


def register_command_class(cls, subparsers, help):
    command_name = guess_command_name(cls)
    parser = subparsers.add_parser(
        command_name, help=help,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.set_defaults(command=cls)
    return parser
