# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

# flake8: noqa

__version__ = '0.1.2-alpha.0'

# Scaffolding functions
from .common import get_config
from .common import get_argument_parser
from .common import handle_parsed_default_args

# Utility classes
from .api import Api
from .idstore import IdStore
from .messagetoemailconverter import MessageToEmailConverter

# MDAs
from .mda import MDA

from .procmailmda import ProcmailMDA
from .stdoutmda import StdoutMDA
