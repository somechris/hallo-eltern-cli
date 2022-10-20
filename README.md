# hallo-eltern-cli

`hallo-eltern-cli` is a command-line/Python/email interface for
[Education Group GmbH](https://www.edugroup.at/)'s
"[Hallo!Eltern](https://hallo-eltern.klassenpinnwand.at/)" application
for Upper-Austrian schools.

`hallo-eltern-cli` is not affiliated with Education Group GmbH or the
"Hallo!Eltern" Application in any way. "Hallo!Eltern" Application is a
product of the Education Group GmbH.

`hallo-eltern-cli` allows to list, messages, read them, download
attachments, etc directly from your Linux terminal and allows to get
full messages including attachments directly to your local inbox.

## Table of Contents

1. [Installation](#installation)
1. [CLI Commands](#cli-commands)
1. [Email Integration](#email-integration)

## Installation

On a Linux-like system with a recent Python (`>=3.7`) run:

```
# Install Python's "requests" library:
sudo apt-get install python3-requests

# Clone this repo:
git clone https://github.com/somechris/hallo-eltern-cli

# Switch to the cloned repo:
cd hallo-eltern-cli

# Configure your credentials:
./halloelterncli.py config --email YOUR-EMAIL@EXAMPLE.ORG --password YOUR-PASSWORD

# Done. \o/

# You can now use the hallo-eltern-cli
# E.g.: List your messages:
./halloelterncli.py list
[...]

Flags |   Id    | Subject
---------------------------------------------------
 CC   | 1234567 | Wandertag am Donnerstag
 CC   | 3456789 | Schikurs Anmeldung
  C   | 2345678 | Fehlendes Arbeitsblatt
```

## CLI commands

The CLI offers the following commands:

* `list` lists available messages
* `show` shows a message
* `open` marks a message as open
* `close` marks a message as closed
* `config` updates and dumps the configuration
* `test` tests the configured user againts the API

## Email integration

`hallo-eltern-cli` comes with `halloeltern4email.py` which allows to
format messages as emails (containing the full message's text and
attachments) and submit them to a mail delivery agent (MDA,
e.g. `procmail`). To run it for example 12 minutes into every hour,
simply add a crontab entry like:

```
12 * * * * /path/to/hallo-eltern-cli/halloeltern4email.py --mode=procmail
```
