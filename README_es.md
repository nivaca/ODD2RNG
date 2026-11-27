# ODD2RNG — esquemas RELAX NG a partir de ODD de TEI, sin abrir oXygen

*(English: [README.md](README.md))*

**Versión 1.3** (`odd2rng.py --version`)

`odd2rng.py` convierte un ODD de TEI en su esquema RELAX NG desde la línea de
órdenes. Ejecuta las mismas dos transformaciones, con los mismos parámetros,
que el escenario *TEI ODD to RELAX NG XML* de oXygen; con las mismas TEI
Stylesheets, el esquema que escribe es idéntico al de oXygen salvo por la
fecha de generación del comentario de cabecera.

```sh
odd2rng.py smed-schema.xml          # escribe out/smed-schema.rng, como oXygen
```

Cómo se hizo se cuenta en [`docs/DESCRIPCIÓN_es.md`](docs/DESCRIPCIÓN_es.md); el
software libre que usa, con la licencia de cada uno, está en
[`docs/THIRD-PARTY_es.md`](docs/THIRD-PARTY_es.md).

## Requisitos

- Python 3.15 o posterior, con la biblioteca `saxonche` (Saxon para Python).
- Las [TEI Stylesheets](https://github.com/TEIC/Stylesheets): un clon del
  repositorio, o la copia que trae oXygen
  (`frameworks/tei/xml/tei/stylesheet`).
- La fuente de TEI, `p5subset.xml`. Un clon de las Stylesheets la tiene en
  `source/`, y oXygen en `frameworks/tei/xml/tei/odd/`; también se puede
  descargar de <https://www.tei-c.org/release/xml/tei/odd/p5subset.xml>.

## Instalación

```sh
git clone https://codeberg.org/nivaca/ODD2RNG.git
cd ODD2RNG
python3 -m pip install --user saxonche      # si tu python3 no la tiene
python3 odd2rng-install.py --stylesheets ~/dev/TEI/Stylesheets
```

`odd2rng-install.py` pone en `~/bin` (en otra carpeta con `--bin CARPETA`) un
enlace simbólico a `odd2rng.py`, para usar la orden desde cualquier carpeta;
un `git pull` en el clon la actualiza. Escribe además el archivo de
configuración, si no existe, con la carpeta indicada en `--stylesheets` (sin
ella, `~/dev/TEI/Stylesheets` si esa carpeta existe). Nunca sobrescribe un
archivo, ni un enlace que apunte a otro sitio salvo con `--force`, y avisa si
`~/bin` no está en el PATH o si `python3` no tiene saxonche. `--uninstall`
quita el enlace y deja el archivo de configuración.

## Configuración

El archivo de configuración es `config.toml`, en la carpeta de ajustes:

| Sistema | Archivo |
|---|---|
| Linux | `~/.config/odd2rng/config.toml` (o bajo `$XDG_CONFIG_HOME`) |
| macOS | `~/Library/Application Support/odd2rng/config.toml` |
| Windows | `%APPDATA%\odd2rng\config.toml` |

`$ODD2RNG_CONFIG` indica otra carpeta. Sus ajustes:

```toml
# Carpeta de las TEI Stylesheets.
stylesheets = "~/dev/TEI/Stylesheets"

# La fuente de TEI; por defecto, source/p5subset.xml en un clon de las
# Stylesheets (u odd/p5subset.xml junto a la carpeta stylesheet de oXygen).
# p5subset = "~/dev/TEI/Stylesheets/source/p5subset.xml"

# Idioma de la documentación del esquema.
# lang = "en"
```

Una ruta relativa en el archivo se toma desde su carpeta. La línea de
órdenes prevalece sobre las variables de entorno `TEI_STYLESHEETS` y
`TEI_P5SUBSET`, y estas sobre el archivo. `odd2rng.py --show-config` muestra
el archivo y las ubicaciones en uso.

## Uso

```
odd2rng.py ODD [-o RNG] [--stylesheets CARPETA] [--p5subset ARCHIVO] [--lang IDIOMA]
odd2rng.py --show-config
odd2rng.py --about
```

| Opción | Significado |
|---|---|
| `ODD` | El ODD que se convierte |
| `-o`, `--output RNG` | Dónde escribir el esquema; por defecto, `out/NOMBRE.rng` junto al ODD, como oXygen |
| `--stylesheets CARPETA` | La carpeta de las TEI Stylesheets, en lugar de la configurada |
| `--p5subset ARCHIVO` | La fuente de TEI, en lugar de la configurada |
| `--lang IDIOMA` | Idioma de la documentación del esquema (por defecto, `en`) |
| `--show-config` | Muestra el archivo de configuración y las ubicaciones en uso |
| `--about` | Qué es el programa, quién lo hizo, su licencia y sus repositorios, y con qué corre aquí: Python, saxonche y Saxon, el archivo de configuración, las TEI Stylesheets y la fuente de TEI |

La última línea de la salida dice si el esquema cambió: *It is new*, *The
schema changed* o *Unchanged apart from the generation date*; en este último
caso no hay nada que valga la pena guardar en git.

## Cómo funciona

El escenario de oXygen es una construcción de Ant (`stylesheet/rng/build-to.xml`
en su marco de TEI) con dos pasos, que `odd2rng.py` ejecuta con Saxon:

1. `odds/odd2odd.xsl` expande el ODD contra la fuente de TEI, con `lang`,
   `defaultSource` (la fuente de TEI), `verbose` y `currentDirectory`;
2. `profiles/default/rng/to.xsl`, que importa `odds/odd2relax.xsl`, convierte
   el ODD expandido en RELAX NG, con los parámetros que pasa oXygen
   (`inputDir`, `lang`, `doclang`, `documentationLanguage`, `displayMode`,
   `directory` y los demás).

Hay dos diferencias con oXygen. El ODD expandido va a una carpeta temporal;
oXygen lo escribe junto al ODD (como `NOMBRE.processedodd`) y luego lo borra.
Y el esquema se escribe en un archivo temporal que después reemplaza al
anterior, de modo que un editor o un validador nunca lo leen a medio
escribir.

La salida se comparó con la de oXygen sobre el ODD del proyecto SMTrad, con
las TEI Stylesheets del propio oXygen (7.60.0) y con un clon más reciente
(7.62.0a): la única diferencia es la fecha de la cabecera.

## Pruebas y versiones

```sh
python3 tools/test.py
```

corre las pruebas a la vez, cada archivo en un proceso propio, tantos a la
vez como procesadores haya (`-j N` lo cambia; `-v` muestra cada archivo a
medida que termina); `python3 -m unittest discover -s tests -v` las corre
una tras otra. Las del programa (`tests/test_odd2rng.py`) corren en una
carpeta temporal, con una
configuración propia, de modo que tus ajustes no cambian nada: el archivo de
configuración y el orden de las ubicaciones, `--about` y `--show-config`,
los mensajes de error y conversiones reales de un ODD pequeño (el esquema,
una segunda pasada que lo encuentra sin cambios, `-o`, un ODD modificado,
uno roto). Las conversiones necesitan las TEI Stylesheets con
`source/p5subset.xml`, de `ODD2RNG_TEST_STYLESHEETS` o de tu archivo de
configuración; comprobar el esquema con documentos necesita lxml. Sin ellos,
esas pruebas se saltan. En GitHub corren en cada *push* y cada lunes, con un
clon de las Stylesheets, así que ninguna se salta.

`python3 tools/release.py` publica la versión de `odd2rng.py`, con las notas
de `CHANGELOG.md`: corre las pruebas, hace el zip, etiqueta, sube a Codeberg
y a GitHub, crea ambas versiones y comprueba las descargas (`--dry-run` se
detiene antes de etiquetar). Es el script de publicación de
[py-schematron](https://codeberg.org/nivaca/py-schematron), que también
conoce este repositorio.

## Licencia

Copyright (C) 2026 Nicolas Vaughan <nicolasvaughan@proton.me>

Este programa es software libre: puede redistribuirlo y/o modificarlo según
los términos de la Licencia Pública General de GNU publicada por la Free
Software Foundation, ya sea la versión 3 de la Licencia o (a su elección)
cualquier versión posterior.

Este programa se distribuye con la esperanza de que sea útil, pero SIN
GARANTÍA ALGUNA; ni siquiera la garantía implícita de COMERCIABILIDAD o de
IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Véase la [Licencia Pública General
de GNU](LICENSE) para más detalles.

El software con que corre y se prueba ODD2RNG conserva sus propias
licencias: véase [`docs/THIRD-PARTY_es.md`](docs/THIRD-PARTY_es.md).
