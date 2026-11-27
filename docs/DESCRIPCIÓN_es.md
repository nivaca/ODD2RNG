# ODD2RNG 1.3: descripción

## Análisis

ODD2RNG es una orden, `odd2rng.py`, que convierte un ODD de TEI en su esquema RELAX NG como lo hace oXygen, sin abrir oXygen. Fue hecha en noviembre de 2026 para los esquemas del proyecto SMTrad, cuyas ediciones se validan contra el RELAX NG generado a partir de un ODD. Es software libre, bajo la Licencia Pública General de GNU, versión 3 o posterior. Lo que usa conserva su licencia: Python, la de la PSF; saxonche (SaxonC-HE), la Mozilla Public License 2.0; las TEI Stylesheets, BSD-2-Clause o CC-BY-SA-3.0, y la fuente de TEI, BSD-2-Clause o CC-BY-3.0. La lista completa, con lo que se usa para probarlo, está en `docs/THIRD-PARTY_es.md`.

Hasta entonces, cada cambio en el esquema smed obligaba a abrir el ODD en oXygen y ejecutar su transformación «TEI ODD to RELAX NG XML». Los requisitos eran tres. El esquema tenía que salir igual que el de oXygen, para que nada cambiara en las ediciones ni en las herramientas que lo leen (py-schematron, VS Code, Emacs y el propio oXygen). Tenía que poder hacerse desde la terminal, con una sola orden y desde cualquier carpeta. Y no podía dejar archivos sueltos en el repositorio del esquema ni un esquema a medio escribir que otro programa pudiera leer en ese momento.

## Diseño

La transformación de oXygen no es una sola hoja de estilo sino una construcción de Ant que viene con su marco de TEI, `stylesheet/rng/build-to.xml`. Tiene dos pasos: `odds/odd2odd.xsl` expande el ODD contra la fuente de TEI, `p5subset.xml`, y `profiles/default/rng/to.xsl`, que importa `odds/odd2relax.xsl`, convierte el ODD expandido en RELAX NG. `odd2rng.py` ejecuta esos mismos dos pasos, con los mismos parámetros, mediante saxonche, el Saxon de Python.

Los archivos del proyecto son estos:

- `odd2rng.py`: la conversión.
- `odd2rng-install.py`: enlaza la orden en `~/bin` y escribe el archivo de configuración si no existe.
- `tools/bundle-zip.py`: hace el zip de cada versión publicada en `build/release/`, que `tools/release.py` borra al publicarla.
- `docs/`: las descripciones.

Dónde están las TEI Stylesheets se decide en este orden: la línea de órdenes (`--stylesheets`, `--p5subset`), las variables de entorno `TEI_STYLESHEETS` y `TEI_P5SUBSET`, o el archivo `config.toml` de la carpeta de ajustes del usuario (`~/.config/odd2rng/` en Linux), como en los demás programas del autor. La fuente de TEI puede omitirse: el script la busca en `source/p5subset.xml` dentro de un clon de las Stylesheets, y en `odd/p5subset.xml` junto a la carpeta de hojas de estilo de oXygen.

## Implementación

Antes de escribir el programa, los dos pasos se ejecutaron a mano con Saxon y el resultado se comparó con el esquema que oXygen acababa de generar: era idéntico salvo por una línea, la fecha del comentario de cabecera («Schema generated from ODD source …»). A partir de ahí el script se limitó a repetir eso, con dos diferencias deliberadas.

### Lo que viene de oXygen

Todo lo que la conversión hace viene del escenario de oXygen: los dos pasos, las hojas de estilo, los parámetros (`lang`, `defaultSource`, `verbose` y `currentDirectory` en el primero; `inputDir`, `lang`, `doclang`, `documentationLanguage`, `displayMode`, `directory` y otros en el segundo) y el lugar del resultado, `out/NOMBRE.rng` junto al ODD. Las hojas de estilo son las del Consorcio TEI; oXygen solo las empaqueta y las llama. Lo propio de ODD2RNG es la carpeta temporal, la escritura atómica, el aviso de si el esquema cambió y la configuración.

### Archivos intermedios y escritura

oXygen escribe el ODD expandido junto al ODD, como `NOMBRE.processedodd`, y lo borra al final; así se explicaba un archivo que se había visto aparecer un momento junto al ODD mientras oXygen estaba abierto. `odd2rng.py` lo escribe en una carpeta temporal. Y el esquema se escribe primero en un archivo temporal que después reemplaza al anterior, de modo que un editor o un validador nunca leen medio esquema.

La última línea de la salida dice si el esquema cambió aparte de la fecha: «It is new», «The schema changed» o «Unchanged apart from the generation date», y en este último caso no hay nada que valga la pena guardar en git. Para saberlo, el script lee el esquema anterior sin su línea de fecha antes de generar el nuevo, y después compara.

### Configuración

La primera versión tomaba las hojas de estilo de la carpeta de oXygen. Pero el autor tiene un clon de las TEI Stylesheets en `~/dev/TEI/Stylesheets`, más nuevo que el de oXygen (7.62.0a frente a 7.60.0), que trae además la fuente de TEI, y el script pasó a usarlo. Cuando el script tuvo repositorio propio, una ruta fija a sus carpetas dejó de tener sentido, y la ubicación pasó al archivo de configuración. Si nada dice dónde están las hojas de estilo, el error nombra el archivo de configuración y muestra la línea que hay que escribir en él; `--show-config` dice qué archivo y qué carpetas están en uso.

### Proceso y distribución

`odd2rng-install.py` pone en `~/bin` un enlace simbólico al script, como hace `py-schematron-install.py` con py-schematron, de modo que la orden funciona desde cualquier carpeta y un `git pull` en el clon la actualiza. Nunca sobrescribe un archivo, ni un enlace que apunte a otro sitio salvo que se le pida, y avisa si `~/bin` no está en el PATH o si `python3` no tiene saxonche. Escribe también el archivo de configuración, si no existe, con la carpeta de hojas de estilo que se le indique. `tools/bundle-zip.py` hace el zip de cada versión con los archivos que git sigue.

## Validación

El esquema que hace el script se comparó con el de oXygen sobre el ODD de smed, con las TEI Stylesheets de oXygen y con el clon más nuevo: en los dos casos la única diferencia es la fecha de la cabecera. El esquema generado da además los mismos resultados al validar con py-schematron la edición latina de SMTrad, de unas 26 000 líneas, y la edición sigue siendo válida contra él con jing.

El instalador y la configuración se probaron en carpetas desechables (con `ODD2RNG_CONFIG` y `--bin`): una primera instalación y una segunda, un archivo y un enlace ajeno ya presentes, `--force`, `--uninstall`, una ruta relativa en la configuración, un archivo que no es TOML, un ajuste desconocido, una carpeta que no es de las TEI Stylesheets y el orden entre la línea de órdenes, el entorno y el archivo. Una conversión tarda unos cinco segundos.

La versión 1.1 convirtió esas comprobaciones en un conjunto de 15 pruebas, que corren en GitHub en cada *push* y cada lunes con un clon recién hecho de las TEI Stylesheets, de modo que un cambio en ellas aparece en menos de una semana. Las pruebas convierten de verdad un ODD pequeño, lo que tarda alrededor de un segundo, y comprueban el esquema con lxml frente a un documento válido y otro que no lo es. La misma versión añadió `--about`, que dice qué Python, qué saxonche, qué archivo de configuración y qué Stylesheets y fuente de TEI usaría el programa.

## Plataforma

Funciona en Linux. Necesita Python 3.15 o superior con saxonche, las TEI Stylesheets (un clon del repositorio del Consorcio TEI o la copia de oXygen) y la fuente de TEI, `p5subset.xml`, que viene en un clon de las Stylesheets y en oXygen, y también se puede descargar del sitio de TEI. No necesita oXygen ni Java.

El archivo de configuración tiene ubicaciones previstas para macOS (`~/Library/Application Support/odd2rng/`) y Windows (`%APPDATA%\odd2rng\`), pero allí no se ha probado. No necesita internet.

## Ambiente

Fue desarrollado en Fedora Linux 45 con KDE Plasma, con Python 3.15 y SaxonC-HE 13.1 (saxonche), y con git, con repositorios en GitHub y Codeberg.

Para usarlo se clona el repositorio o se descomprime el zip de una versión publicada, se instala saxonche (`python3 -m pip install --user saxonche`) y se ejecuta `python3 odd2rng-install.py --stylesheets CARPETA`, que deja la orden `odd2rng.py` en `~/bin` y la configuración en `~/.config/odd2rng/config.toml`. Después basta `odd2rng.py esquema.xml`.
