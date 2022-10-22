#!/bin/bash
# This file is part of hallo-eltern-cli and licensed under the
# Apache License Version 2.0 (See LICENSE.txt)
# SPDX-License-Identifier: Apache-2.0

# To skip over this skript, set the environment variable to something non-empty
# E.g.:
#
#   export SKIP_PRE_COMMIT=y
#

set -e
set -o pipefail

maintenance/check-headers.sh
maintenance/check-versions.sh
