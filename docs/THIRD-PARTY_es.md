Software libre que usa ODD2RNG
==============================

ODD2RNG es software libre, bajo la Licencia Pública General de GNU, versión
3 o posterior (GPL-3.0-or-later).  Lo forman solo sus propios scripts:
ninguno de los programas de abajo está copiado en este repositorio ni en el
zip de las versiones.  Se instalan aparte, con pip o con el gestor de
paquetes del sistema, o los clona el usuario, y cada uno conserva su
licencia.

Con qué corre el programa
-------------------------

| Software | Para qué se usa | Licencia |
|---|---|---|
| [Python](https://www.python.org/) 3.15 o posterior, con su biblioteca estándar (`tomllib` lee el archivo de configuración) | El lenguaje de `odd2rng.py` y `odd2rng-install.py` | Python Software Foundation License (PSF-2.0) |
| [saxonche](https://pypi.org/project/saxonche/) (SaxonC-HE, de Saxonica) | Ejecuta las dos transformaciones XSLT, `odd2odd.xsl` y `to.xsl`, con XInclude | Mozilla Public License 2.0 (MPL-2.0) |
| [TEI Stylesheets](https://github.com/TEIC/Stylesheets): `odds/odd2odd.xsl`, `profiles/default/rng/to.xsl`, `odds/odd2relax.xsl` y las hojas que importan | Expanden el ODD y lo convierten en RELAX NG.  No se distribuyen con ODD2RNG: el usuario indica una copia, la de oXygen o un clon | Doble licencia: BSD-2-Clause o Creative Commons Atribución-CompartirIgual 3.0 (CC-BY-SA-3.0), a elección del usuario |
| La fuente de [TEI P5](https://github.com/TEIC/TEI), `p5subset.xml` | Las Guías de TEI contra las que se expande el ODD; viene con las TEI Stylesheets o se indica aparte | Doble licencia: BSD-2-Clause o Creative Commons Atribución 3.0 (CC-BY-3.0) |

oXygen XML Editor, cuya transformación «TEI ODD to RELAX NG XML» reproduce
ODD2RNG, no es software libre y no hace falta para usarlo; solo se empleó
para comparar los esquemas.

Con qué se prueba
-----------------

Nada de esto hace falta para usar ODD2RNG, y nada se distribuye con él.

| Software | Para qué se usa | Licencia |
|---|---|---|
| [lxml](https://lxml.de/) | Comprueba el esquema generado frente a un documento válido y otro que no lo es, en las pruebas | BSD-3-Clause |
| [libxml2](https://gitlab.gnome.org/GNOME/libxml2) y [libxslt](https://gitlab.gnome.org/GNOME/libxslt) | Las bibliotecas en C bajo lxml (incluidas en sus wheels) | MIT |
| [jing](https://relaxng.org/jclark/jing.html), de James Clark | Validó a mano la edición de SMTrad contra el esquema generado | BSD-3-Clause (Thai Open Source Software Center) |
| [py-schematron](https://codeberg.org/nivaca/py-schematron) | Comprobó que la edición da los mismos resultados con el esquema nuevo | GPL-3.0-or-later |
| [GitHub Actions](https://github.com/features/actions): `actions/checkout`, `actions/setup-python` | Ejecutan las pruebas en cada *push* y cada lunes | MIT |
| [Git](https://git-scm.com/) | Clona las TEI Stylesheets para las pruebas en GitHub y da la lista de archivos del zip (`tools/bundle-zip.py`) | GPL-2.0 |
| [tea](https://gitea.com/gitea/tea) y [GitHub CLI](https://cli.github.com/) (`gh`) | Hacen las versiones en Codeberg y GitHub (`tools/release.py`) | MIT |
