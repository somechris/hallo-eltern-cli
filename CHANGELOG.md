# Unreleased

* Breaking Change: Split `mta` command into `stdout` and `mda` commands
* Breaking Change: Require Python `>=3.7`
* Enhancement: Add `help` command
* Enhancement: Add `smtp` command
* Enhancement: Add `--force-address` to email generating commands
* Enhancement: Add `--mda-command` to `mda` command
* Enhancement: Add `--separator` to `stdout` command
* Enhancement: Add `--version` argument
* Enhancement: Add `version` command

### [1.0.0](https://github.com/somechris/hallo-eltern-cli/releases/tag/v1.0.0) (2022-10-23)

* Breaking Change: Move `hallo-eltern4email` script into cli as `mta` command
* Enhancement: Use dynamic version in `User-Agent` header
* Enhancement: Show defaults in command specific help pages
* Fix: Correctly decode doubly encoded titles and messages
* Fix: Avoid fetching attachments when showing messages

### [0.1.1](https://github.com/somechris/hallo-eltern-cli/releases/tag/v0.1.1) (2022-10-22)

* Fix: `hallo-eltern4email` does not start due to missing parameter

### [0.1.0](https://github.com/somechris/hallo-eltern-cli/releases/tag/v0.1.0) (2022-10-21)

* Initial release
