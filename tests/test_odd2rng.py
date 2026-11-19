# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Nicolas Vaughan <nicolasvaughan@proton.me>
# This file is part of ODD2RNG. See the LICENSE file for details.
"""Tests of odd2rng.py: python3 -m unittest discover -s tests -v

They run the script in a temporary folder, with a configuration folder of
their own (ODD2RNG_CONFIG) and without TEI_STYLESHEETS or TEI_P5SUBSET, so
the user's own settings change nothing.  The conversions need the TEI
Stylesheets, a clone of https://github.com/TEIC/Stylesheets (which has the
TEI source, source/p5subset.xml): they are found through the variable
ODD2RNG_TEST_STYLESHEETS, or else the user's own configuration; without
them those tests are skipped.  Checking the generated schema against
documents needs lxml; without it that test is skipped.
"""

import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "odd2rng.py"
TEI = "http://www.tei-c.org/ns/1.0"

ODD = f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="{TEI}" xml:lang="en">
  <teiHeader><fileDesc><titleStmt><title>tiny</title></titleStmt>
    <publicationStmt><p>p</p></publicationStmt><sourceDesc><p>s</p></sourceDesc>
  </fileDesc></teiHeader>
  <text><body>
    <schemaSpec ident="tiny" start="TEI">
      <moduleRef key="tei"/>
      <moduleRef key="core" include="p title"/>
      <moduleRef key="header" include="teiHeader fileDesc titleStmt publicationStmt sourceDesc"/>
      <moduleRef key="textstructure" include="TEI text body"/>
    </schemaSpec>
  </body></text>
</TEI>
"""


def document(body: str) -> str:
    return (f'<TEI xmlns="{TEI}"><teiHeader><fileDesc><titleStmt><title>t</title></titleStmt>'
            f'<publicationStmt><p>p</p></publicationStmt><sourceDesc><p>s</p></sourceDesc>'
            f'</fileDesc></teiHeader><text><body>{body}</body></text></TEI>')


def user_stylesheets():
    """The TEI Stylesheets for the conversion tests, or None."""
    if os.environ.get("ODD2RNG_TEST_STYLESHEETS"):
        d = Path(os.environ["ODD2RNG_TEST_STYLESHEETS"]).expanduser()
    else:
        base = Path(os.environ.get("ODD2RNG_CONFIG") or
                    Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "odd2rng")
        try:
            with open(base / "config.toml", "rb") as f:
                value = tomllib.load(f).get("stylesheets")
        except (OSError, tomllib.TOMLDecodeError):
            return None
        if not value:
            return None
        d = Path(value).expanduser()
        d = d if d.is_absolute() else base / d
    ok = (d / "odds/odd2odd.xsl").is_file() and (d / "source/p5subset.xml").is_file()
    return d.resolve() if ok else None


STYLESHEETS = user_stylesheets()


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="odd2rng-test-")
        self.dir = Path(self._tmp.name)
        self.config = self.dir / "config"
        self.config.mkdir()
        self.env = {k: v for k, v in os.environ.items()
                    if k not in ("TEI_STYLESHEETS", "TEI_P5SUBSET")}
        self.env["ODD2RNG_CONFIG"] = str(self.config)

    def tearDown(self):
        self._tmp.cleanup()

    def run_script(self, *args, env=None):
        """Run odd2rng.py; return (exit code, stdout, stderr)."""
        p = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                           capture_output=True, text=True, cwd=self.dir, timeout=300,
                           env={**self.env, **(env or {})})
        return p.returncode, p.stdout, p.stderr

    def write_config(self, text: str):
        (self.config / "config.toml").write_text(text, encoding="utf-8")

    def fake_stylesheets(self, name="Stylesheets", p5subset=True) -> Path:
        """A folder that looks like the TEI Stylesheets (no working XSLT)."""
        d = self.dir / name
        (d / "odds").mkdir(parents=True)
        (d / "odds/odd2odd.xsl").write_text("<x/>")
        if p5subset:
            (d / "source").mkdir()
            (d / "source/p5subset.xml").write_text("<x/>")
        return d


class TestInformation(Base):
    def test_version(self):
        code, out, _ = self.run_script("--version")
        self.assertEqual(code, 0)
        self.assertRegex(out.strip(), r"^odd2rng\.py \d+\.\d+$")

    def test_about(self):
        code, out, _ = self.run_script("--about")
        self.assertEqual(code, 0)
        self.assertRegex(out.splitlines()[0], r"^odd2rng\.py \d+\.\d+$")
        for expected in ("Nicolas Vaughan <nicolasvaughan@proton.me>",
                         "GNU General Public License", "https://codeberg.org/nivaca/ODD2RNG",
                         "Python:", "saxonche:", str(self.config / "config.toml"),
                         "(does not exist)", "TEI Stylesheets: not found"):
            self.assertIn(expected, out)

    def test_about_shows_the_locations_in_use(self):
        d = self.fake_stylesheets()
        code, out, _ = self.run_script("--about", "--stylesheets", d)
        self.assertEqual(code, 0)
        self.assertIn(f"TEI Stylesheets: {d.resolve()}", out)
        self.assertIn(f"TEI source:      {(d / 'source/p5subset.xml').resolve()}", out)

    def test_show_config(self):
        d = self.fake_stylesheets()
        self.write_config(f'stylesheets = "{d}"\nlang = "es"\n')
        code, out, _ = self.run_script("--show-config")
        self.assertEqual(code, 0, out)
        self.assertIn(f"TEI Stylesheets: {d.resolve()}", out)
        self.assertIn("Language:        es", out)


class TestConfiguration(Base):
    def test_where_the_stylesheets_come_from(self):
        """--stylesheets, then TEI_STYLESHEETS, then the configuration file;
        a relative path in the file is taken from the file's folder."""
        a, b = self.fake_stylesheets("a"), self.fake_stylesheets("b")
        c = self.fake_stylesheets("config/c")
        self.write_config('stylesheets = "c"\n')
        for args, env, expected in ((["--stylesheets", a], {"TEI_STYLESHEETS": str(b)}, a),
                                    ([], {"TEI_STYLESHEETS": str(b)}, b),
                                    ([], {}, c)):
            code, out, err = self.run_script("--show-config", *args, env=env)
            self.assertEqual(code, 0, err)
            self.assertIn(f"TEI Stylesheets: {expected.resolve()}", out)

    def test_p5subset_from_oxygens_layout(self):
        d = self.fake_stylesheets("frameworks/stylesheet", p5subset=False)
        (d.parent / "odd").mkdir()
        (d.parent / "odd/p5subset.xml").write_text("<x/>")
        code, out, err = self.run_script("--show-config", "--stylesheets", d)
        self.assertEqual(code, 0, err)
        self.assertIn(f"TEI source:      {(d.parent / 'odd/p5subset.xml').resolve()}", out)

    def test_no_stylesheets(self):
        code, _, err = self.run_script("--show-config")
        self.assertNotEqual(code, 0)
        self.assertIn("Where are the TEI Stylesheets?", err)

    def test_not_a_stylesheets_folder(self):
        code, _, err = self.run_script("--show-config", "--stylesheets", self.dir)
        self.assertNotEqual(code, 0)
        self.assertIn("has no odds/odd2odd.xsl", err)

    def test_no_p5subset(self):
        d = self.fake_stylesheets(p5subset=False)
        code, _, err = self.run_script("--show-config", "--stylesheets", d)
        self.assertNotEqual(code, 0)
        self.assertIn("Cannot find p5subset.xml", err)

    def test_bad_configuration_files(self):
        for text, message in (('stylesheets = "x\n', "is not valid TOML"),
                              ('styelsheets = "x"\n', "unknown setting(s) styelsheets"),
                              ("lang = 3\n", "lang must be a string")):
            self.write_config(text)
            code, _, err = self.run_script("--show-config")
            self.assertNotEqual(code, 0, text)
            self.assertIn(message, err)

    def test_the_odd_is_required_and_must_exist(self):
        code, _, err = self.run_script()
        self.assertEqual(code, 2)
        self.assertIn("the ODD is required", err)
        code, _, err = self.run_script("missing.xml")
        self.assertNotEqual(code, 0)
        self.assertIn("No such ODD", err)


@unittest.skipUnless(STYLESHEETS, "no TEI Stylesheets (with source/p5subset.xml) for the conversions")
class TestConversion(Base):
    def setUp(self):
        super().setUp()
        self.write_config(f'stylesheets = "{STYLESHEETS}"\n')
        self.odd = self.dir / "tiny.xml"
        self.odd.write_text(ODD, encoding="utf-8")
        self.rng = self.dir / "out" / "tiny.rng"

    def test_conversion_and_rerun(self):
        code, out, err = self.run_script(self.odd)
        self.assertEqual(code, 0, err)
        self.assertTrue(self.rng.is_file())
        self.assertIn("It is new.", out)
        text = self.rng.read_text(encoding="utf-8")
        self.assertIn("http://relaxng.org/ns/structure/1.0", text)
        self.assertIn("Schema generated from ODD source", text)
        for name in ("TEI", "teiHeader", "body", "p"):
            self.assertIn(f'name="{name}"', text)
        self.assertNotIn('name="div"', text)               # (not included)
        # nothing is left beside the ODD or in out/ but the schema
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()),
                         ["config", "out", "tiny.xml"])
        self.assertEqual([p.name for p in self.rng.parent.iterdir()], ["tiny.rng"])
        code, out, err = self.run_script(self.odd)
        self.assertEqual(code, 0, err)
        self.assertIn("Unchanged apart from the generation date.", out)

    def test_output_option_and_change(self):
        target = self.dir / "elsewhere" / "s.rng"
        code, _, err = self.run_script(self.odd, "-o", target)
        self.assertEqual(code, 0, err)
        self.assertTrue(target.is_file())
        self.odd.write_text(ODD.replace('include="p title"', 'include="p title hi"'),
                            encoding="utf-8")
        code, out, err = self.run_script(self.odd, "-o", target)
        self.assertEqual(code, 0, err)
        self.assertIn("The schema changed.", out)
        self.assertIn('name="hi"', target.read_text(encoding="utf-8"))

    def test_the_schema_validates(self):
        try:
            from lxml import etree
        except ImportError:
            self.skipTest("lxml is not installed")
        code, _, err = self.run_script(self.odd)
        self.assertEqual(code, 0, err)
        schema = etree.RelaxNG(etree.parse(str(self.rng)))
        self.assertTrue(schema.validate(etree.fromstring(document("<p>a</p>"))),
                        schema.error_log)
        self.assertFalse(schema.validate(etree.fromstring(document("<div><p>a</p></div>"))))

    def test_a_broken_odd_fails(self):
        self.odd.write_text("<TEI xmlns='http://www.tei-c.org/ns/1.0'><not-closed></TEI>")
        code, _, err = self.run_script(self.odd)
        self.assertNotEqual(code, 0)
        self.assertIn("odd2odd.xsl failed", err)
        self.assertFalse(self.rng.exists())


if __name__ == "__main__":
    unittest.main()
