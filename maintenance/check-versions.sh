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

cd "$(dirname "$0")"
cd ..

WARNINGS=0

VERSION=$(grep '^\(\[tool\.poetry\]\|version *=\)' pyproject.toml | grep -A 1 '^\[tool\.poetry\]' | tail -n 1 | sed -e 's/^.*=[[:space:]]*"\([^"]*\)".*/\1/')
VERSION_LINE="__version__ = '$VERSION'"

warn() {
    echo "WARNING:" "$@" >&2
    echo >&2
    WARNINGS=$((WARNINGS+1))
}

check_version() {
    local INIT_FILE="$1"
    if ! grep --quiet "^$VERSION_LINE\$" "$INIT_FILE"
    then
        if ! grep --quiet '^from .* import __version__' "$INIT_FILE"
        then
            warn "Failed to find \"$VERSION_LINE\" (or a __version__ import) in \"$INIT_FILE\""
        fi
    fi
}

check_version_init_files() {
    for INIT_FILE in $(find \( -name '.tox' -prune \) -o \( -name 'tests' -prune \) -o \( -type f -name '__init__.py' -print \) )
    do
        check_version "$INIT_FILE"
    done
}

check_version_init_files

if [ "$WARNINGS" != 0 ]
then
    echo "Found $WARNINGS warnings. Aborting." >&2
    exit 1
fi
