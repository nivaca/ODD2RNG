# Registro de cambios

Los cambios notables de ODD2RNG. Las versiones, con sus archivos zip, están
en [Codeberg](https://codeberg.org/nivaca/ODD2RNG/releases) y
[GitHub](https://github.com/nivaca/ODD2RNG/releases).

## Sin publicar

- `tools/zenodo.py`: la descripción del depósito es ahora el README entero
  de la etiqueta, en HTML. El borrador recibe además el colaborador (el
  director del proyecto), los idiomas, el copyright, el repositorio en
  GitHub, el lenguaje de programación y el estado del desarrollo; estos
  últimos, por la API de registros de Zenodo, porque la de depósitos no los
  admite. El token puede guardarse en el llavero del escritorio
  (`secret-tool store --label="Zenodo token" service zenodo`) en vez de en
  `$ZENODO_TOKEN`; `tools/zenodo.py check-token` dice si hay uno.

- `tools/zenodo.py` prepara el depósito de una versión en Zenodo. `collect`
  deja en `dist/zenodo/` el árbol de la etiqueta como
  `ODD2RNG-VERSIÓN-source.tar.gz`, con su firma, un `SHA256SUMS` del
  depósito, firmado, y la clave pública, y comprueba cada firma con solo esa
  clave (`--packages` añade los archivos de la versión). `upload` lo sube a
  Zenodo como borrador, versión nueva del depósito si ya lo hay, y nunca lo
  publica. `tools/release.py` reúne ahora el depósito después de la etiqueta
  y lo sube como borrador, salvo con `--no-zenodo`. Los metadatos están en
  `.zenodo.json`.
- `tools/zenodo.py`: la descripción del depósito deja fuera la línea que
  lleva a los README en otras lenguas y la sección Screenshots, cuyas
  imágenes Zenodo no muestra.
- `tools/release.py` publica ahora cada versión en Zenodo
  (`tools/zenodo.py upload --publish`), en vez de dejar un borrador;
  `--zenodo-draft` todavía lo deja. `tools/zenodo.py publish` publica un
  borrador que ya está allí (por omisión, el que espera con el título del
  proyecto).
- `tools/test.py` corre las pruebas a la vez, cada archivo de `tests/` en
  un proceso propio, tantos a la vez como procesadores haya (`-j N`), los
  más lentos primero; así las corre `tools/release.py`.

## 1.3 — 2026-11-21

- `docs/THIRD-PARTY_es.md` (y `docs/THIRD-PARTY.md`, en inglés): el software
  libre que usa ODD2RNG, y la licencia de cada uno, desde aquello con lo que
  corre (Python, saxonche, las TEI Stylesheets y la fuente de TEI) hasta
  aquello con que se prueba y se publica.
- La conversión no cambia.

## 1.2 — 2026-11-19

- py-xmlvalidate, el validador de Schematron que lee la configuración de
  ODD2RNG, pasa a llamarse py-schematron; los enlaces y `tools/release.py`
  cambian con él.
- La conversión no cambia.

## 1.1 — 2026-11-19

- `odd2rng.py --about` dice qué es el programa, quién lo hizo, su licencia
  y sus repositorios, y con qué se ejecuta en este equipo: Python,
  saxonche y Saxon, el archivo de configuración, y las TEI Stylesheets y la
  fuente de TEI que usaría (o por qué no las encontró).
- Pruebas (`tests/`, 15): la configuración y el orden de las ubicaciones,
  los mensajes y conversiones reales de un ODD pequeño. Se ejecutan en
  GitHub con cada push y cada lunes, con un clon de las TEI Stylesheets.
- `tools/release.py` publica una versión con una sola orden.
- La conversión no cambia.

## 1.0 — 2026-11-17

- Primera versión: el esquema RELAX NG a partir de un ODD de TEI, tal como
  lo hace la transformación "TEI ODD to RELAX NG XML" de oXygen, con un
  archivo de configuración para las TEI Stylesheets, la fuente de TEI y el
  idioma, y un instalador.
