#!/usr/bin/env python3
"""Genera la versión "cuerpo" de la app para publicarla como Artifact.

`index.html` ya es un único archivo autocontenido: trae fflate embebido y no
depende de nada externo, así que para tener una copia portátil alcanza con
copiarlo tal cual. Este script existe sólo para el formato de Artifact de
claude.ai, que espera el contenido SIN el envoltorio del documento (<!doctype>,
<head>, <body>), porque lo agrega el anfitrión.

    python3 tools/build_artifact.py salida.html              # cuerpo (Artifact)
    python3 tools/build_artifact.py salida.html --completo   # documento entero

Sobre el envoltorio de fflate
-----------------------------
La librería viene en formato UMD, que decide cómo exportarse según el entorno:

    typeof module   != 'undefined' && typeof exports == 'object' ? module.exports = f()
  : typeof define   != 'undefined' && define.amd               ? define(f)
  : (self || this).fflate = f()

Si la página anfitriona ya define `define.amd` o `module`/`exports`, fflate se
registra ahí y NUNCA crea la global `fflate`; la app falla entonces con
"fflate is not defined" al abrir un .mzML comprimido o al armar un .zip. Por eso
en index.html la librería está envuelta en una función que declara `define`,
`module` y `exports` como variables locales sin valor: el UMD las ve como
`undefined`, toma la última rama y asigna la global. Ese aislamiento vive en
index.html, no acá; este script sólo lo arrastra junto con el resto.
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / 'index.html'


def construir(solo_cuerpo: bool) -> str:
    html = ORIGEN.read_text(encoding='utf-8')

    estilo = re.search(r'<style>.*?</style>', html, re.S).group(0)
    cuerpo = re.search(r'<body>(.*?)</body>', html, re.S).group(1)

    if solo_cuerpo:
        return estilo + '\n' + cuerpo

    titulo = re.search(r'<title>(.*?)</title>', html, re.S)
    titulo = titulo.group(1) if titulo else 'Convertidor de espectros VITEK MS'
    return (
        '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{titulo}</title>\n{estilo}\n</head>\n<body>{cuerpo}</body>\n</html>\n'
    )


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit('Uso: build_artifact.py <salida.html> [--completo]')
    salida = Path(sys.argv[1])
    completo = '--completo' in sys.argv[2:]
    contenido = construir(solo_cuerpo=not completo)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(contenido, encoding='utf-8')

    # La app tiene que quedar autocontenida: ningún archivo servido aparte y
    # la librería efectivamente adentro, con su envoltorio UMD aislado.
    assert '<script src="' not in contenido, 'quedó un script externo sin embeber'
    assert '<link rel="stylesheet"' not in contenido, 'quedó una hoja de estilos externa'
    assert 'unzlibSync' in contenido, 'fflate no quedó embebido'
    assert 'var define, module, exports;' in contenido, 'falta el aislamiento del UMD'
    print(f'OK: {salida} ({len(contenido) // 1024} KB, '
          f'{"documento completo" if completo else "cuerpo para Artifact"})')


if __name__ == '__main__':
    main()
