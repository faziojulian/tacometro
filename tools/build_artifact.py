#!/usr/bin/env python3
"""Genera una versión de un solo archivo de la app, con fflate embebido.

Sirve para publicar la app donde no se pueden servir archivos aparte (por
ejemplo, un Artifact de claude.ai) y para tener una copia portátil que
funcione offline con solo abrir el .html.

Sobre el envoltorio de fflate
-----------------------------
fflate viene en formato UMD, que decide cómo exportarse según el entorno:

    typeof module   != 'undefined' && typeof exports == 'object' ? module.exports = f()
  : typeof define   != 'undefined' && define.amd               ? define(f)
  : (self || this).fflate = f()

Si la página que aloja el HTML ya define `define.amd` (un cargador AMD) o
`module`/`exports`, fflate se registra ahí y NUNCA crea la global `fflate`.
La app falla entonces con "fflate is not defined" al abrir un .mzML con
arrays comprimidos con zlib, un .gz, o al exportar los CSV en .zip.

Por eso embebemos la librería dentro de una función que declara `define`,
`module` y `exports` como variables locales sin valor: así el UMD ve esos
nombres como `undefined`, toma la última rama y asigna la global en `self`.
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / 'index.html'
VENDOR = RAIZ / 'vendor' / 'fflate.umd.min.js'
TAG_VENDOR = '<script src="vendor/fflate.umd.min.js"></script>'


def envolver_fflate(codigo: str) -> str:
    """Aísla el UMD para que siempre exporte la global `fflate`."""
    return (
        '<script>\n'
        '(function(){\n'
        '// Ver tools/build_artifact.py: sombreamos estos nombres para que el\n'
        '// UMD de fflate no se registre en un cargador de módulos de la página\n'
        '// anfitriona y cree siempre la global `fflate`.\n'
        'var define, module, exports;\n'
        + codigo +
        '\n})();\n'
        '</script>'
    )


def construir(solo_cuerpo: bool) -> str:
    html = ORIGEN.read_text(encoding='utf-8')
    fflate = VENDOR.read_text(encoding='utf-8')

    estilo = re.search(r'<style>.*?</style>', html, re.S).group(0)
    cuerpo = re.search(r'<body>(.*?)</body>', html, re.S).group(1)

    if TAG_VENDOR not in cuerpo:
        sys.exit('ERROR: no se encontró el <script> de fflate en index.html')
    cuerpo = cuerpo.replace(TAG_VENDOR, envolver_fflate(fflate))

    if solo_cuerpo:
        # Formato Artifact: solo estilo + contenido del body (el host agrega
        # <!doctype>, <head> y <body>).
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

    assert 'vendor/fflate' not in contenido, 'quedó una referencia externa a fflate'
    assert 'unzlibSync' in contenido, 'fflate no quedó embebido'
    print(f'OK: {salida} ({len(contenido) // 1024} KB, '
          f'{"documento completo" if completo else "cuerpo para Artifact"})')


if __name__ == '__main__':
    main()
