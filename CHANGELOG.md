# Changelog

All notable changes to ODD2RNG. The releases, with their zip files, are on
[Codeberg](https://codeberg.org/nivaca/ODD2RNG/releases) and
[GitHub](https://github.com/nivaca/ODD2RNG/releases).

## 1.2 — 2026-11-19

- py-xmlvalidate, the Schematron validator that reads ODD2RNG's
  configuration, is renamed py-schematron: the links and
  `tools/release.py` follow.
- The conversion does not change.

## 1.1 — 2026-11-19

- `odd2rng.py --about` says what the program is, who made it, its licence
  and repositories, and what it runs with here: Python, saxonche and Saxon,
  the configuration file, and the TEI Stylesheets and TEI source it would
  use (or why they were not found).
- Tests (`tests/`, 15): the configuration and the order of the locations,
  the messages, and real conversions of a small ODD. They run on GitHub at
  every push and every Monday, with a clone of the TEI Stylesheets.
- `tools/release.py` makes a release in one command.
- The conversion does not change.

## 1.0 — 2026-11-17

- First version: the RELAX NG schema from a TEI ODD, as oXygen's "TEI ODD
  to RELAX NG XML" transformation makes it, with a configuration file for
  the TEI Stylesheets, the TEI source and the language, and an installer.
