Open-source software used by ODD2RNG
====================================

ODD2RNG is free software, under the GNU General Public License, version 3
or later (GPL-3.0-or-later).  It is made of its own scripts only: none of
the programs below is copied into this repository or into the release zip.
They are installed separately, by pip or by the system's package manager,
or cloned by the user, and each keeps its own licence.

What the program runs with
--------------------------

| Software | What it is used for | Licence |
|---|---|---|
| [Python](https://www.python.org/) 3.15 or later, with its standard library (`tomllib` reads the configuration file) | The language of `odd2rng.py` and `odd2rng-install.py` | Python Software Foundation License (PSF-2.0) |
| [saxonche](https://pypi.org/project/saxonche/) (SaxonC-HE, by Saxonica) | Runs the two XSLT transformations, `odd2odd.xsl` and `to.xsl`, with XInclude | Mozilla Public License 2.0 (MPL-2.0) |
| [TEI Stylesheets](https://github.com/TEIC/Stylesheets): `odds/odd2odd.xsl`, `profiles/default/rng/to.xsl`, `odds/odd2relax.xsl` and the stylesheets they import | Expand the ODD and turn it into RELAX NG.  They are not distributed with ODD2RNG: the user points to a copy, oXygen's or a clone | Dual licence: BSD-2-Clause or Creative Commons Attribution-ShareAlike 3.0 (CC-BY-SA-3.0), at the user's choice |
| [TEI P5](https://github.com/TEIC/TEI) source, `p5subset.xml` | The TEI Guidelines against which the ODD is expanded; it comes with the TEI Stylesheets, or is given apart | Dual licence: BSD-2-Clause or Creative Commons Attribution 3.0 (CC-BY-3.0) |

oXygen XML Editor, whose "TEI ODD to RELAX NG XML" transformation ODD2RNG
reproduces, is not open-source software and is not needed to run it; it
was used only to compare the schemas.

What is used to test it
-----------------------

These are not needed to run ODD2RNG, and none of them is distributed with
it.

| Software | What it is used for | Licence |
|---|---|---|
| [lxml](https://lxml.de/) | Checks the generated schema against a valid and an invalid document, in the tests | BSD-3-Clause |
| [libxml2](https://gitlab.gnome.org/GNOME/libxml2) and [libxslt](https://gitlab.gnome.org/GNOME/libxslt) | The C libraries under lxml (included in its wheels) | MIT |
| [jing](https://relaxng.org/jclark/jing.html), by James Clark | Checked the SMTrad edition against the generated schema, by hand | BSD-3-Clause (Thai Open Source Software Center) |
| [py-schematron](https://codeberg.org/nivaca/py-schematron) | Checked that the edition gives the same results with the new schema | GPL-3.0-or-later |
| [GitHub Actions](https://github.com/features/actions): `actions/checkout`, `actions/setup-python` | Run the tests at every push and every Monday | MIT |
| [Git](https://git-scm.com/) | Clones the TEI Stylesheets for the tests on GitHub, and lists the files of the release zip (`tools/bundle-zip.py`) | GPL-2.0 |
| [tea](https://gitea.com/gitea/tea) and [GitHub CLI](https://cli.github.com/) (`gh`) | Make the releases on Codeberg and GitHub (`tools/release.py`) | MIT |
