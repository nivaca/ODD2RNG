# ODD2RNG — RELAX NG schemas from TEI ODDs, without opening oXygen

*(Español: [README_es.md](README_es.md))*

**Version 1.0** (`odd2rng.py --version`)

`odd2rng.py` turns a TEI ODD into its RELAX NG schema from the command line.
It runs the same two transformations, with the same parameters, as oXygen's
*TEI ODD to RELAX NG XML* scenario, so with the same TEI Stylesheets the
schema it writes is identical to oXygen's except for the generation date in
its header comment.

```sh
odd2rng.py smed-schema.xml          # writes out/smed-schema.rng, as oXygen does
```

How it was made is told in [`docs/DESCRIPTION.md`](docs/DESCRIPTION.md).

## Requirements

- Python 3.15 or later, with the `saxonche` library (Saxon for Python).
- The [TEI Stylesheets](https://github.com/TEIC/Stylesheets): a clone of the
  repository, or the copy inside oXygen
  (`frameworks/tei/xml/tei/stylesheet`).
- The TEI source, `p5subset.xml`. A clone of the Stylesheets has it in
  `source/`, and oXygen in `frameworks/tei/xml/tei/odd/`; it can also be
  downloaded from <https://www.tei-c.org/release/xml/tei/odd/p5subset.xml>.

## Installation

```sh
git clone https://codeberg.org/nivaca/ODD2RNG.git
cd ODD2RNG
python3 -m pip install --user saxonche      # if your python3 does not have it
python3 odd2rng-install.py --stylesheets ~/dev/TEI/Stylesheets
```

`odd2rng-install.py` puts a symbolic link to `odd2rng.py` in `~/bin` (another
folder with `--bin FOLDER`), so the command works from any folder, and a `git
pull` in the clone updates it. It also writes the configuration file, if
there is none, with the folder given in `--stylesheets` (without it,
`~/dev/TEI/Stylesheets` if that folder exists). It never overwrites a file,
nor a link that points elsewhere unless `--force` is given, and it says
whether `~/bin` is on the PATH and whether `python3` has saxonche.
`--uninstall` removes the link and leaves the configuration file.

## Configuration

The configuration file is `config.toml` in the settings folder:

| System | File |
|---|---|
| Linux | `~/.config/odd2rng/config.toml` (or under `$XDG_CONFIG_HOME`) |
| macOS | `~/Library/Application Support/odd2rng/config.toml` |
| Windows | `%APPDATA%\odd2rng\config.toml` |

`$ODD2RNG_CONFIG` names another folder. Its settings:

```toml
# Folder of the TEI Stylesheets.
stylesheets = "~/dev/TEI/Stylesheets"

# The TEI source; by default source/p5subset.xml in a Stylesheets clone
# (or odd/p5subset.xml beside oXygen's stylesheet folder).
# p5subset = "~/dev/TEI/Stylesheets/source/p5subset.xml"

# Language of the documentation in the schema.
# lang = "en"
```

A relative path in the file is taken from the file's folder. The command
line wins over the environment variables `TEI_STYLESHEETS` and
`TEI_P5SUBSET`, and these win over the file. `odd2rng.py --show-config`
shows the file and the locations in use.

## Usage

```
odd2rng.py ODD [-o RNG] [--stylesheets DIR] [--p5subset FILE] [--lang LANG]
odd2rng.py --show-config
odd2rng.py --about
```

| Option | Meaning |
|---|---|
| `ODD` | The ODD to convert |
| `-o`, `--output RNG` | Where to write the schema; by default `out/NAME.rng` next to the ODD, as oXygen does |
| `--stylesheets DIR` | The TEI Stylesheets folder, instead of the configured one |
| `--p5subset FILE` | The TEI source, instead of the configured one |
| `--lang LANG` | Language of the documentation in the schema (default `en`) |
| `--show-config` | Show the configuration file and the locations in use |
| `--about` | What the program is, who made it, its licence and repositories, and what it runs with here: Python, saxonche and Saxon, the configuration file, the TEI Stylesheets and source |

The last line of the output says whether the schema changed: *It is new*,
*The schema changed*, or *Unchanged apart from the generation date*, in
which case there is nothing worth committing.

## How it works

oXygen's scenario is an Ant build (`stylesheet/rng/build-to.xml` in its TEI
framework) with two steps, which `odd2rng.py` runs with Saxon:

1. `odds/odd2odd.xsl` expands the ODD against the TEI source, with `lang`,
   `defaultSource` (the TEI source), `verbose` and `currentDirectory`;
2. `profiles/default/rng/to.xsl`, which imports `odds/odd2relax.xsl`, turns
   the expanded ODD into RELAX NG, with the parameters oXygen passes
   (`inputDir`, `lang`, `doclang`, `documentationLanguage`, `displayMode`,
   `directory` and the rest).

Two things differ from oXygen. The expanded ODD goes to a temporary folder,
whereas oXygen writes it next to the ODD (as `NAME.processedodd`) and
deletes it afterwards. And the schema is written to a temporary file that
then replaces the old one, so an editor or a validator never reads it
half-written.

The output was compared with oXygen's on the SMTrad project's ODD, both with
oXygen's own TEI Stylesheets (7.60.0) and with a newer clone (7.62.0a): the
only difference is the date in the header.

## Tests and releases

```sh
python3 -m unittest discover -s tests -v
```

runs the tests (`tests/test_odd2rng.py`) in a temporary folder, with a
configuration of their own, so your settings change nothing: the
configuration file and the order of the locations, `--about` and
`--show-config`, the error messages, and real conversions of a small ODD
(the schema, a second run that finds it unchanged, `-o`, a changed ODD, a
broken one). The conversions need the TEI Stylesheets with
`source/p5subset.xml`, from `ODD2RNG_TEST_STYLESHEETS` or your
configuration file; checking the schema against documents needs lxml.
Without them those tests are skipped. On GitHub they run at every push and
every Monday, with a clone of the Stylesheets, so none is skipped.

`python3 tools/release.py` releases the version in `odd2rng.py`, with the
notes of `CHANGELOG.md`: it runs the tests, makes the zip, tags, pushes to
Codeberg and GitHub, makes both releases and checks the downloads
(`--dry-run` stops before tagging). It is the release script of
[py-schematron](https://codeberg.org/nivaca/py-schematron), which knows
this repository too.

## License

Copyright (C) 2026 Nicolas Vaughan <nicolasvaughan@proton.me>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the [GNU General Public License](LICENSE) for more
details.
