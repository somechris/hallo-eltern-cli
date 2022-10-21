# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

import json
import os


class IdStore(object):
    def __init__(self, file):
        self._file = file
        self._ids = {}

        self._load()

    def _load(self):
        if os.path.isfile(self._file):
            with open(self._file, 'r') as f:
                self._ids = json.load(f)

    def persist(self):
        os.makedirs(os.path.dirname(self._file), exist_ok=True)
        with open(self._file, "w") as f:
            f.write(json.dumps(self._ids))

    def __contains__(self, id):
        return id in self._ids

    def __setitem__(self, id, value=True):
        self._ids[id] = value
