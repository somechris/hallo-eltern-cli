# hallo-eltern-cli

[![Tests](https://github.com/somechris/hallo-eltern-cli/workflows/Tests/badge.svg)](https://github.com/somechris/hallo-eltern-cli/actions?query=workflow%3ATests)

`hallo-eltern-cli` is a command-line/Python/email interface for
[Education Group GmbH](https://www.edugroup.at/)'s
"[Hallo!Eltern](https://hallo-eltern.klassenpinnwand.at/)" application
for Upper-Austrian schools.

`hallo-eltern-cli` is not affiliated with Education Group GmbH or their
"Hallo!Eltern" application in any way. The "Hallo!Eltern" application is a
product of the Education Group GmbH.

`hallo-eltern-cli` allows to list, messages, read them, download
attachments, etc directly from your Linux terminal and allows to get
full messages including attachments directly to your local inbox.

## Table of Contents

1. [Installation](#installation)
1. [CLI Commands](#cli-commands)
1. [Email Integration](#email-integration)

## Installation

You need Python `>=3.6`

1. Install the package:

   ```
   pip3 install hallo-eltern-cli
   ```

1. Set the credentials from your "Hallo!Eltern" application:

    ```
    hallo-eltern-cli config --email YOUR-EMAIL@EXAMPLE.ORG --password YOUR-PASSWORD
    ```

1. Done \o/

`hallo-eltern-cli` is now ready for use. For example to list messages,
use the `list` command:

```
hallo-eltern-cli list
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

`hallo-eltern-cli` comes with `hallo-eltern4email` which allows to
format messages as emails (containing the full message's text and
attachments) and submit them to a mail delivery agent (MDA,
e.g. `procmail`). To run it for example 12 minutes into every hour,
simply add a crontab entry like:

```
12 * * * * /path/to/hallo-eltern4email --mode=procmail
```
