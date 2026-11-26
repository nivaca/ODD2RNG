# Changelog

All notable changes to ODD2RNG. The releases, with their zip files, are on
[Codeberg](https://codeberg.org/nivaca/ODD2RNG/releases) and
[GitHub](https://github.com/nivaca/ODD2RNG/releases).

## Unreleased

- `tools/zenodo.py`: the description of the deposit is now the whole
  README of the tag, in HTML. The draft also gets the contributor (the
  project leader), the languages, the copyright, the repository on GitHub,
  the programming language and the development status, these last through
  Zenodo's records API (its deposit API doesn't take them). The token can
  be kept in the desktop keyring (`secret-tool store --label="Zenodo
  token" service zenodo`) instead of `$ZENODO_TOKEN`; `tools/zenodo.py
  check-token` says whether there is one.

- `tools/zenodo.py` prepares the deposit of a release for Zenodo. `collect`
  puts in `dist/zenodo/` the tree of the tag as
  `ODD2RNG-VERSION-source.tar.gz`, with its signature, a signed `SHA256SUMS`
  of the deposit and the public key, and checks every signature with only
  that key (`--packages` adds the files of the release). `upload` sends it
  to Zenodo as a draft, a new version of the deposit if there is one
  already, and never publishes it. `tools/release.py` now collects the
  deposit after the tag and uploads it as a draft, unless `--no-zenodo`. The
  metadata are in `.zenodo.json`.
- `tools/zenodo.py`: the description of the deposit leaves out the line
  that points to the README in other languages and the Screenshots section,
  whose images Zenodo does not show.
- `tools/release.py` now publishes each release on Zenodo
  (`tools/zenodo.py upload --publish`), instead of leaving a draft;
  `--zenodo-draft` still leaves one. `tools/zenodo.py publish` publishes a
  draft already there (by default the one waiting with the project's title).

## 1.3 — 2026-11-21

- `docs/THIRD-PARTY.md` (and `docs/THIRD-PARTY_es.md`, in Spanish): the
  open-source software ODD2RNG uses, and the licence of each, from what it
  runs with (Python, saxonche, the TEI Stylesheets and the TEI source) to
  what it is tested and released with.
- The conversion does not change.

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
