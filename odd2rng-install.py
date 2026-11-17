#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Nicolas Vaughan <nicolasvaughan@proton.me>
# This file is part of ODD2RNG. See the LICENSE file for details.
"""Install odd2rng.py: python3 odd2rng-install.py [--bin FOLDER]
[--stylesheets DIR] [--force | --uninstall]

Makes a symbolic link in ~/bin (or FOLDER) to odd2rng.py in this folder, so
it can be run from anywhere by its name:

    odd2rng.py smed-schema.xml

The link points to this folder, so a `git pull` here updates the command at
once.  Run it again after moving this folder.

It also creates the configuration file, if there is none, with the folder of
the TEI Stylesheets: the one given with --stylesheets, else
~/dev/TEI/Stylesheets if it exists; otherwise the file is written with that
line commented out, to be filled in.  An existing configuration file is never
changed.

Nothing else is touched: an existing file of the same name in FOLDER is left
alone (and reported), and so is a link that points somewhere else, unless
--force is given.  --uninstall removes only the link that points to this
folder, and leaves the configuration file.

The script runs with the `python3` it finds first on the PATH, which needs
the saxonche library.  The installer checks that, and says how to install it
if it is missing.  Everything goes into the user's own folders: no
administrator rights are needed.
"""

import sys

if sys.version_info < (3, 15):
    sys.exit(f"odd2rng-install.py needs Python 3.15 or later; this is "
             f"Python {sys.version.split()[0]}.")

import argparse  # noqa: E402
import importlib.util  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import stat  # noqa: E402
import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
SCRIPT = "odd2rng.py"
DEFAULT_STYLESHEETS = "~/dev/TEI/Stylesheets"


def say(text: str = ""):
    print(text, flush=True)


def odd2rng():
    """odd2rng.py as a module, for its configuration functions."""
    spec = importlib.util.spec_from_file_location("odd2rng", HERE / SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ours(link: Path) -> bool:
    """Whether LINK is a symbolic link to this folder's script."""
    return link.is_symlink() and Path(os.path.realpath(link)) == HERE / SCRIPT


def install(folder: Path, force: bool) -> bool:
    folder.mkdir(parents=True, exist_ok=True)
    target, link = HERE / SCRIPT, folder / SCRIPT
    mode = target.stat().st_mode
    target.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if ours(link):
        say(f"  {link} already points here")
        return True
    if link.is_symlink() and (force or not link.exists()):
        link.unlink()                              # (another or a broken link)
    elif link.exists() or link.is_symlink():
        what = "a link to " + os.readlink(link) if link.is_symlink() else "a file"
        say(f"  {link} is {what}: left alone (--force replaces a link, never a file)")
        return False
    link.symlink_to(target)
    say(f"  {link} -> {target}")
    return True


def uninstall(folder: Path):
    link = folder / SCRIPT
    if ours(link):
        link.unlink()
        say(f"  removed {link}")
    elif link.exists() or link.is_symlink():
        say(f"  {link} does not point here: left alone")
    else:
        say(f"  {link} does not exist")


def write_config(stylesheets: str | None):
    module = odd2rng()
    path = module.config_path()
    if path.exists():
        say(f"\nThe configuration file {path} exists: left as it is.")
        return
    chosen = stylesheets or (DEFAULT_STYLESHEETS
                             if Path(DEFAULT_STYLESHEETS).expanduser().is_dir() else None)
    if chosen and not (Path(chosen).expanduser() / "odds/odd2odd.xsl").is_file():
        sys.exit(f"{chosen} is not a TEI Stylesheets folder: it has no odds/odd2odd.xsl.")
    line = (f'stylesheets = "{chosen}"' if chosen else
            f'# stylesheets = "{DEFAULT_STYLESHEETS}"')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# odd2rng.py settings (see odd2rng.py --help)\n"
        "\n"
        "# Folder of the TEI Stylesheets: a clone of https://github.com/TEIC/Stylesheets\n"
        "# or oXygen's frameworks/tei/xml/tei/stylesheet.\n"
        f"{line}\n"
        "\n"
        "# The TEI source; by default source/p5subset.xml in a Stylesheets clone\n"
        "# (or odd/p5subset.xml beside oXygen's stylesheet folder).\n"
        '# p5subset = "~/dev/TEI/Stylesheets/source/p5subset.xml"\n'
        "\n"
        "# Language of the documentation in the schema.\n"
        '# lang = "en"\n', encoding="utf-8")
    if chosen:
        say(f"\nWrote {path}, with the TEI Stylesheets in {chosen}.")
    else:
        say(f"\nWrote {path}.  Edit its `stylesheets` line to say where the TEI "
            f"Stylesheets are (or run this again with --stylesheets DIR after deleting it).")


def check_path(folder: Path):
    dirs = [Path(p).resolve() for p in os.environ.get("PATH", "").split(os.pathsep) if p]
    if folder.resolve() not in dirs:
        say(f"\nNote: {folder} is not on your PATH, so the command needs its full path.")
        say(f"  Add it, e.g. in bash: export PATH=\"{folder}:$PATH\" (in ~/.bashrc);")
        say(f"  in fish: fish_add_path {folder}")


def check_python():
    """The interpreter the script's first line (#!/usr/bin/env python3) finds."""
    python = shutil.which("python3")
    if not python:
        say("\nNote: there is no python3 on the PATH; the script needs one (3.15 or later).")
        return
    probe = subprocess.run([python, "-c", "import sys, saxonche; "
                            "print(sys.version.split()[0])"], capture_output=True, text=True)
    if probe.returncode == 0:
        say(f"\nThe script will run with {python} (Python {probe.stdout.strip()}), "
            f"which has saxonche.")
        return
    say(f"\nNote: the script will run with {python}, which "
        + ("does not have the 'saxonche' library." if "saxonche" in probe.stderr
           else "cannot run it yet:\n" + probe.stderr.strip()))
    say(f"  Install it for that Python:  {python} -m pip install --user saxonche")
    say("  or put first on your PATH a Python that has it (such as a virtual\n"
        "  environment's bin/ folder).")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="odd2rng-install.py",
        description="Link the command odd2rng.py into ~/bin (or another folder), and "
                    "create its configuration file if there is none.")
    parser.add_argument("--bin", type=Path, default=Path.home() / "bin", metavar="FOLDER",
                        help="where to put the link (default: ~/bin)")
    parser.add_argument("--stylesheets", metavar="DIR",
                        help="the TEI Stylesheets folder to write in a new configuration "
                             f"file (default: {DEFAULT_STYLESHEETS}, if it exists)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--force", action="store_true",
                       help="replace an existing link that points elsewhere (never a file)")
    group.add_argument("--uninstall", action="store_true",
                       help="remove the link that points to this folder")
    args = parser.parse_args(argv)
    folder = args.bin.expanduser()
    if args.uninstall:
        say(f"Removing the link in {folder}:")
        uninstall(folder)
        return
    say(f"Linking the command into {folder}:")
    ok = install(folder, args.force)
    write_config(args.stylesheets)
    check_path(folder)
    check_python()
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
