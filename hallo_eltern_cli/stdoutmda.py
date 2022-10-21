# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

from . import MDA


class StdoutMDA(MDA):
    def deliver(self, message):
        print(message)
