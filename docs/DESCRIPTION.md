How ODD2RNG was made
====================

ODD2RNG is a command, `odd2rng.py`, that turns a TEI ODD into its RELAX NG
schema the way oXygen does, without opening oXygen.  Nicolas Vaughan made
it in November 2026 for the schemas of the SMTrad project, whose editions
are checked against the RELAX NG generated from an ODD.  It is free
software, under the GNU General Public License, version 3 or later.  Here
I explain how it was made, in four stages.


1. What oXygen does
-------------------

Until then, every change to the smed schema meant opening the ODD in
oXygen and running its "TEI ODD to RELAX NG XML" transformation.  That
transformation is not a single stylesheet but an Ant build that ships with
oXygen's TEI framework, `stylesheet/rng/build-to.xml`, and I read it, with
the scenario that calls it, to see what it does.  It has two steps.  The
first, `odds/odd2odd.xsl`, expands the ODD against the TEI source,
`p5subset.xml`, with four parameters (`lang`, `defaultSource`, `verbose`
and `currentDirectory`), and writes the result next to the ODD, as
`NAME.processedodd`.  The second, `profiles/default/rng/to.xsl`, which
imports `odds/odd2relax.xsl`, turns that expanded ODD into RELAX NG, with
some ten more parameters; the build then deletes the `.processedodd`
file.  This explained a file I had seen appear for a moment next to the
ODD, while oXygen was open.

Before writing any program, I ran the two steps by hand with Saxon, with
the same parameters, and compared the result with the schema oXygen had
just made.  It was identical except for one line, the date in the header
comment ("Schema generated from ODD source ...").


2. The script
-------------

`odd2rng.py` does those two steps with saxonche, Saxon for Python.  By
default it writes `out/NAME.rng` next to the ODD, where oXygen writes it,
and `-o` gives another place.  Two things are done differently.  The
expanded ODD goes to a temporary folder, not next to the ODD, so nothing
appears in the schema's repository even for a moment.  And the schema is
written to a temporary file that then replaces the old one, so an editor
or a validator that reads it at that moment never sees half a schema.

The last line of the output says whether the schema changed apart from
that date: "It is new", "The schema changed", or "Unchanged apart from
the generation date", in which case there is nothing worth committing.
Before generating, the script reads the old schema without its date line;
afterwards it compares.


3. Where the stylesheets are
----------------------------

The first version took the TEI Stylesheets and `p5subset.xml` from
oXygen's own folder.  But I keep a clone of the TEI Stylesheets in
`~/dev/TEI/Stylesheets`, newer than oXygen's (7.62.0a against 7.60.0),
and it also brings the TEI source, in `source/p5subset.xml`.  So the
script was made to take the stylesheets from that clone and, by default,
the TEI source from the same folder.

When the script got a repository of its own, a fixed path to my folders
no longer made sense.  The location now comes, in this order, from the
command line (`--stylesheets`, `--p5subset`), from the environment
variables `TEI_STYLESHEETS` and `TEI_P5SUBSET`, or from a configuration
file, `config.toml`, in the user's settings folder
(`~/.config/odd2rng/` on Linux), as in my other programs.  The TEI source
can be left out: the script looks for `source/p5subset.xml` in a clone and
for `odd/p5subset.xml` beside oXygen's stylesheet folder.  If nothing says
where the stylesheets are, the error names the configuration file and
shows the line to write in it, and `--show-config` tells which file and
which folders are in use.


4. Installation and distribution
--------------------------------

`odd2rng-install.py` puts a symbolic link to the script in `~/bin`, as
`py-schematron-install.py` does for py-schematron, so the command works
from any folder and a `git pull` in the clone updates it.  It never
overwrites a file, nor a link that points elsewhere unless asked, and it
says whether `~/bin` is on the PATH and whether `python3` has saxonche.
It also writes the configuration file, if there is none, with the
stylesheet folder given to it.  `tools/bundle-zip.py` makes the zip of
each release from the files that git tracks.


Testing
-------

The schema the script makes was compared with oXygen's on the smed ODD,
with oXygen's TEI Stylesheets and with the newer clone: in both cases the
only difference is the date in the header.  The schema it makes also
gives the same results when the SMTrad Latin edition (about 26,000
lines) is checked with py-schematron, and the edition stays valid
against it with jing.  The installer and the configuration were tried in
throwaway folders (with `ODD2RNG_CONFIG` and `--bin`): a first install,
a second one, a file and a foreign link already in place, `--force`,
`--uninstall`, a relative path in the configuration, a file that is not
TOML, an unknown setting, a folder that is not the TEI Stylesheets, and
the order of the command line, the environment and the file.  A
conversion takes about five seconds.  The program has three files, about
560 lines.

Version 1.1 turned those checks into a test suite of 15 tests, which run
on GitHub at every push and every Monday with a fresh clone of the TEI
Stylesheets, so that a change upstream shows up within a week.  The
suite converts a small ODD for real, which takes about a second, and
checks the schema against a valid and an invalid document with lxml.
The same version added `--about`, which says which Python, saxonche,
configuration file, Stylesheets and TEI source the program would use.
