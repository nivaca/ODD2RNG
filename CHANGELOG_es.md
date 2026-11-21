# Registro de cambios

Los cambios notables de ODD2RNG. Las versiones, con sus archivos zip, están
en [Codeberg](https://codeberg.org/nivaca/ODD2RNG/releases) y
[GitHub](https://github.com/nivaca/ODD2RNG/releases).

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
