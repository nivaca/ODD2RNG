#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Nicolas Vaughan <nicolasvaughan@proton.me>
# This file is part of ODD2RNG. See the LICENSE file for details.
"""Generate the RELAX NG schema from a TEI ODD, as oXygen's "TEI ODD to
RELAX NG XML" transformation does.

    odd2rng.py ODD [-o OUT] [--stylesheets DIR] [--p5subset FILE] [--lang LANG]
    odd2rng.py --show-config
    odd2rng.py --about

For example, odd2rng.py smed-schema.xml writes out/smed-schema.rng next to
the ODD, where oXygen writes it.

The two steps are oXygen's own (stylesheet/rng/build-to.xml in its TEI
framework), with the same parameters:

1. odds/odd2odd.xsl expands the ODD against the TEI source, p5subset.xml;
2. profiles/default/rng/to.xsl (which imports odds/odd2relax.xsl) turns the
   expanded ODD into RELAX NG.

With the same TEI Stylesheets and TEI source as oXygen, the result is
identical to oXygen's except for the date in its header comment ("Schema
generated from ODD source ...").

Where the TEI Stylesheets are, in this order: --stylesheets, the
environment variable TEI_STYLESHEETS, or `stylesheets` in the configuration
file.  The TEI source likewise: --p5subset, TEI_P5SUBSET, `p5subset` in the
configuration file, or else source/p5subset.xml in a Stylesheets checkout
(or odd/p5subset.xml beside oXygen's stylesheet folder).  The configuration
file is config.toml in the settings folder ($ODD2RNG_CONFIG names another):

    Linux     $XDG_CONFIG_HOME/odd2rng/config.toml (usually ~/.config)
    macOS     ~/Library/Application Support/odd2rng/config.toml
    Windows   %APPDATA%\\odd2rng\\config.toml

for example:

    stylesheets = "~/dev/TEI/Stylesheets"
    # p5subset = "~/dev/TEI/Stylesheets/source/p5subset.xml"
    # lang = "en"

Unlike oXygen, the expanded ODD goes to a temporary folder, not next to the
ODD, and the schema is written atomically (to a temporary file that then
replaces it), so an editor or validator never reads it half-written.  At the
end the script says whether the schema changed apart from that date.

Needs Python 3.15 or later with saxonche (pip install saxonche).
"""

import sys

if sys.version_info < (3, 15):
    sys.exit(f"odd2rng.py needs Python 3.15 or later; this is "
             f"Python {sys.version.split()[0]}.")

import argparse  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
import tomllib  # noqa: E402
from pathlib import Path  # noqa: E402

__version__ = "1.1"

STAMP = re.compile(r"Schema generated from ODD source [^\n]*")
CONFIG_KEYS = {"stylesheets", "p5subset", "lang"}


def config_dir() -> Path:
    """The settings folder: $ODD2RNG_CONFIG, else the system's usual one."""
    if os.environ.get("ODD2RNG_CONFIG"):
        return Path(os.environ["ODD2RNG_CONFIG"]).expanduser()
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "odd2rng"


def config_path() -> Path:
    return config_dir() / "config.toml"


def load_config() -> dict:
    """The configuration file's settings ({} if there is no file)."""
    path = config_path()
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        return {}
    except tomllib.TOMLDecodeError as e:
        sys.exit(f"{path} is not valid TOML: {e}")
    unknown = set(data) - CONFIG_KEYS
    if unknown:
        sys.exit(f"{path}: unknown setting(s) {', '.join(sorted(unknown))}; "
                 f"the settings are {', '.join(sorted(CONFIG_KEYS))}.")
    for key, value in data.items():
        if not isinstance(value, str):
            sys.exit(f"{path}: {key} must be a string, in quotes.")
    return data


def sources(arg, env_var, config, key):
    """Where a location may come from, in order: (value, origin, path)."""
    for value, origin in ((arg, f"--{key}"), (os.environ.get(env_var), env_var),
                          (config.get(key), str(config_path()))):
        if value:
            p = Path(value).expanduser()
            if origin == str(config_path()) and not p.is_absolute():
                p = config_dir() / p           # relative to the configuration file
            yield p, origin


def find_stylesheets(arg, config) -> Path:
    for d, origin in sources(arg, "TEI_STYLESHEETS", config, "stylesheets"):
        if not (d / "odds/odd2odd.xsl").is_file():
            sys.exit(f"{d} (from {origin}) is not a TEI Stylesheets folder: "
                     f"it has no odds/odd2odd.xsl.")
        return d.resolve()
    sys.exit(f"Where are the TEI Stylesheets?  Give their folder with --stylesheets, "
             f"or set it once in {config_path()}:\n\n"
             f'    stylesheets = "~/dev/TEI/Stylesheets"\n\n'
             f"(a clone of https://github.com/TEIC/Stylesheets, or oXygen's "
             f"frameworks/tei/xml/tei/stylesheet).")


def find_p5subset(arg, config, stylesheets: Path) -> Path:
    for f, origin in sources(arg, "TEI_P5SUBSET", config, "p5subset"):
        if not f.is_file():
            sys.exit(f"{f} (from {origin}) does not exist.")
        return f.resolve()
    candidates = [stylesheets / "source/p5subset.xml",        # a Stylesheets checkout
                  stylesheets.parent / "odd/p5subset.xml"]    # oXygen's layout
    for f in candidates:
        if f.is_file():
            return f.resolve()
    sys.exit(f"Cannot find p5subset.xml, the TEI source (looked for "
             f"{' and '.join(str(c) for c in candidates)}).  Give it with --p5subset, "
             f"or set p5subset in {config_path()}; it can be downloaded from "
             f"https://www.tei-c.org/release/xml/tei/odd/p5subset.xml")


def without_stamp(path: Path) -> str | None:
    """The schema's text without its generation date, or None if absent."""
    try:
        return STAMP.sub("", path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def generate(odd: Path, out: Path, stylesheets: Path, p5subset: Path, lang: str):
    from saxonche import PySaxonApiError, PySaxonProcessor

    def transform(proc, xslt, stylesheet, params, source, target):
        try:
            exe = xslt.compile_stylesheet(stylesheet_file=str(stylesheet))
            for name, value in params.items():
                exe.set_parameter(name, proc.make_string_value(value))
            exe.transform_to_file(source_file=str(source), output_file=str(target))
        except PySaxonApiError as e:
            sys.exit(f"{stylesheet.name} failed: {e}")
        if not target.is_file() or target.stat().st_size == 0:
            sys.exit(f"{stylesheet.name} produced no output.")

    with PySaxonProcessor(license=False) as proc, \
            tempfile.TemporaryDirectory(prefix="odd2rng-") as tmp:
        proc.set_configuration_property("http://saxon.sf.net/feature/xinclude-aware", "true")
        xslt = proc.new_xslt30_processor()
        expanded = Path(tmp) / (odd.name + ".processedodd")
        print(f"Expanding {odd.name} against {p5subset} ...", flush=True)
        transform(proc, xslt, stylesheets / "odds/odd2odd.xsl",
                  {"lang": lang, "defaultSource": str(p5subset), "verbose": "false",
                   "currentDirectory": str(odd.parent)},
                  odd, expanded)
        print(f"Generating RELAX NG with {stylesheets} ...", flush=True)
        out.parent.mkdir(parents=True, exist_ok=True)
        fd, partial = tempfile.mkstemp(prefix=out.name + ".", suffix=".tmp", dir=out.parent)
        os.close(fd)
        try:
            transform(proc, xslt, stylesheets / "profiles/default/rng/to.xsl",
                      {"inputDir": str(odd.parent) + "/", "lang": lang, "doclang": lang,
                       "documentationLanguage": lang, "verbose": "false",
                       "logoFile": "_slidelogo.png", "summaryDoc": "false",
                       "displayMode": "rnc", "directory": str(out.parent)},
                      expanded, Path(partial))
            os.replace(partial, out)
        finally:
            if os.path.exists(partial):
                os.unlink(partial)


def show_config(args, config):
    path = config_path()
    print(f"Configuration file: {path}" + ("" if path.is_file() else " (does not exist)"))
    for key in sorted(config):
        print(f"  {key} = {config[key]!r}")
    stylesheets = find_stylesheets(args.stylesheets, config)
    print(f"TEI Stylesheets: {stylesheets}")
    print(f"TEI source:      {find_p5subset(args.p5subset, config, stylesheets)}")
    print(f"Language:        {args.lang or config.get('lang') or 'en'}")


def about(args) -> str:
    """The text of --about: what this is, whose, its licence and where it
    lives, and what it runs with here (Python, saxonche and Saxon, the
    configuration file, the TEI Stylesheets and source it would use)."""
    from importlib.metadata import PackageNotFoundError, version

    def located(find):
        try:
            return str(find())
        except SystemExit as e:                  # (not found: say why)
            why = str(e.code).splitlines()[0]
            if why.startswith("Where are"):      # (nothing given anywhere)
                why = "give them with --stylesheets, TEI_STYLESHEETS or the configuration file"
            return f"not found: {why}"
    try:
        saxonche = version("saxonche")
        from saxonche import PySaxonProcessor
        with PySaxonProcessor(license=False) as proc:
            saxonche += f" ({proc.version})"
    except (PackageNotFoundError, ImportError):
        saxonche = "not installed (pip install saxonche)"
    config = load_config()
    stylesheets = located(lambda: find_stylesheets(args.stylesheets, config))
    p5subset = (located(lambda: find_p5subset(args.p5subset, config, Path(stylesheets)))
                if not stylesheets.startswith("not found") else "(needs the Stylesheets)")
    path = config_path()
    return f"""odd2rng.py {__version__}
RELAX NG schemas from TEI ODDs, made as oXygen's "TEI ODD to RELAX NG XML"
transformation makes them, with the TEI Stylesheets and Saxon.

Author:          Nicolas Vaughan <nicolasvaughan@proton.me>
Licence:         GNU General Public License, version 3 or later
Code:            https://codeberg.org/nivaca/ODD2RNG
                 https://github.com/nivaca/ODD2RNG

This script:     {Path(__file__).resolve()}
Python:          {sys.version.split()[0]} ({sys.executable})
saxonche:        {saxonche}
Configuration:   {path}{"" if path.is_file() else " (does not exist)"}
TEI Stylesheets: {stylesheets}
TEI source:      {p5subset}"""


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="odd2rng.py",
        description="Generate the RELAX NG schema from a TEI ODD, as oXygen does.",
        epilog=f"Configuration file: {config_path()}")
    parser.add_argument("odd", nargs="?", type=Path, help="the ODD")
    parser.add_argument("-o", "--output", type=Path, metavar="RNG",
                        help="where to write the schema (default: out/NAME.rng next to the ODD)")
    parser.add_argument("--stylesheets", metavar="DIR",
                        help="the TEI Stylesheets folder (default: from TEI_STYLESHEETS "
                             "or the configuration file)")
    parser.add_argument("--p5subset", metavar="FILE",
                        help="the TEI source, p5subset.xml (default: from TEI_P5SUBSET, the "
                             "configuration file, or source/p5subset.xml in the Stylesheets)")
    parser.add_argument("--lang", help="documentation language (default: en)")
    parser.add_argument("--show-config", action="store_true",
                        help="show the configuration file and the locations in use, and exit")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--about", action="store_true",
                        help="what this program is, whose, its licence and where it lives, "
                             "and what it runs with here; then exit")
    args = parser.parse_args(argv)
    if args.about:
        print(about(args))
        return
    config = load_config()

    if args.show_config:
        show_config(args, config)
        return
    if args.odd is None:
        parser.error("the ODD is required")
    odd = args.odd.expanduser().resolve()
    if not odd.is_file():
        sys.exit(f"No such ODD: {odd}")
    out = (args.output.expanduser().resolve() if args.output
           else odd.parent / "out" / (odd.stem + ".rng"))
    stylesheets = find_stylesheets(args.stylesheets, config)
    p5subset = find_p5subset(args.p5subset, config, stylesheets)
    lang = args.lang or config.get("lang") or "en"

    before = without_stamp(out)
    start = time.perf_counter()
    generate(odd, out, stylesheets, p5subset, lang)
    after = without_stamp(out)
    print(f"Wrote {out} ({out.stat().st_size // 1024} KB, {time.perf_counter() - start:.1f} s).")
    if before is None:
        print("It is new.")
    elif before == after:
        print("Unchanged apart from the generation date.")
    else:
        print("The schema changed.")


if __name__ == "__main__":
    main()
