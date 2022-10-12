#!/bin/bash

SCRIPT_DIR_ABS="$(dirname "$0")"

exec /usr/bin/env python3 "$SCRIPT_DIR_ABS"/halloelterncli/halloelterncli.py "$@"
