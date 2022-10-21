# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import subprocess

from . import MDA


class ProcmailMDA(MDA):
    def deliver(self, message):
        subprocess.run(["/usr/bin/procmail"],
                       input=str(message),
                       text=True,
                       check=True)
