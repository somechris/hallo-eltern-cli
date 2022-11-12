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
    1. [Email server (SMTP)](#email-server-smtp)
    1. [Mail Delivery Agent (MDA)](#mail-delivery-agent-mda)

## Installation

You need Python `>=3.7`

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
* `mda` feeds messages into a message delivery agend (procmail, maildrop, ...)
* `stdout` dumps messages to stdout
* `smtp` sends messages as emails
* `version` prints the version number

## Email integration

Simple ways to integrate `hallo-eltern-cli` with your email pipelines
are to either

* [forward the messages to an email server (SMTP)](#email-server-smtp)
    (e.g.: gmx, office365, local server), or to
* [pipe the messages to a message delivery agent
    (MDA)](#mail-delivery-agent-mda) (e.g.: `procmail`, `maildrop`).

### Email server (SMTP)

The `smtp` mode of `hallo-eltern-cli` allows to send the messages
(containing the full message's text and attachments) to an email
server to get them to your usual email inbox.

To run check for new messages and forward them to your inbox for
example 12 minutes into every hour, simply add a crontab entry like:

```
12 * * * * /path/to/hallo-eltern-cli smtp --force-address your-email-address@example.org
```

and configure the email server to use in `$HOME/.config/hallo-eltern-cli/config`

* Local SMTP server

    The default configuration of `hallo-eltern-cli` is to submit to a
    local SMTP server through `localhost:25`. So you do not need to add
    any configuration.

* GMX

    To submit the messages to your GMX inbox, set the `[smtp]` section
    in your `$HOME/.config/hallo-eltern-cli/config` to:

    ```
    [smtp]
    host = mail.gmx.net
    port = 587
    starttls = True
    user = your-email-address@gmx.at
    password = your-secret-password
    ```

    (Note that the password gets stored in plain text, so secure your
    config file through external means)

* Office365 / Hotmail

    To submit the messages to your Office365 or Hotmail inbox, set the
    `[smtp]` section in your `$HOME/.config/hallo-eltern-cli/config`
    to:

    ```
    [smtp]
    host = smtp.office365.com
    port = 587
    starttls = True
    user = your-email-address@hotmail.com
    password = your-secret-password
    ```

    (Note that the password gets stored in plain text, so secure your
    config file through external means)


### Mail Delivery Agent (MDA)

The `mda` mode of `hallo-eltern-cli` allows to format messages as
emails (containing the full message's text and attachments) and submit
them to a mail delivery agent (MDA, e.g. `procmail`). To run it for
example 12 minutes into every hour, simply add a crontab entry like:

```
12 * * * * /path/to/hallo-eltern-cli mda
```
