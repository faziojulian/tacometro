# tacometro
Tacometro

## mzML → XML MicrobeNet

`mzml-a-microbenet.html` convierte archivos `.mzML` (corridas de VITEK MS PRIME) en:

- una lista de picos (m/z + intensidad), extraída y verificable con el estándar abierto mzML (HUPO-PSI);
- un archivo `.xml` "borrador" pensado para importar en MicrobeNet (CDC).

**Importante:** MicrobeNet espera el XML que exporta el software Bruker MALDI Biotyper
(carpeta `HT-Out`). No fue posible confirmar el esquema exacto de ese XML (el sitio
`microbenet.cdc.gov` no es accesible desde este entorno y no se contó con un archivo de
ejemplo ya aceptado), así que el XML generado es una plantilla editable que **hay que
validar contra un archivo real** antes de usarla para importar datos. El mapeo de campos
vive en la función `buildDraftXml` dentro del archivo, para ajustarlo fácilmente. Mientras
tanto, el CSV de picos es la salida confiable.

Todo el procesamiento ocurre en el navegador (sin subir archivos a ningún servidor), usando
[fflate](https://github.com/101arrowz/fflate) (vendorizado en `vendor/`) para descomprimir
los arrays binarios `zlib`/`gzip` del mzML.
