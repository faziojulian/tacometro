# Convertidor de archivos bioMérieux

Convierte archivos `.mzML` de corridas VITEK MS PRIME (bioMérieux) a un XML pensado para
importar en MicrobeNet (CDC), y a una lista de picos en CSV.

> Nota: el nombre del repositorio en GitHub todavía es `tacometro`. GitHub no permite
> renombrarlo por API/token de esta integración, así que hay que hacerlo a mano desde
> **Settings → General → Repository name** (sugerencia de slug: `convertidor-biomerieux`).

## `index.html` — conversor mzML → XML MicrobeNet

`index.html` es la página principal (se sirve en la raíz de GitHub Pages). Convierte uno o
varios archivos `.mzML` de VITEK MS PRIME en:

- una lista de picos (m/z + intensidad) por muestra, extraída y verificable con el estándar abierto mzML (HUPO-PSI), exportable en CSV;
- un único archivo `.xml` de **proyecto** (`<MspMatchResult>`, con un `<Analyte>` por muestra) pensado para importar en MicrobeNet (CDC).

**Esquema del XML:** la estructura (`MspMatchResult` > `ProjectInfo` + `Analytes` >
`Analyte` > `Peaklist` > `Peaks` > `Peak`, con sus atributos e intensidades normalizadas
0–1) se tomó de un archivo `.xml` real ya aceptado por MicrobeNet, no es una suposición.
Quedan dos puntos que sí son best-effort y conviene revisar:

- el nombre de cada `Analyte` (`name`/`externId`) se reconstruye combinando campos del
  `.mzML` según el patrón observado en ese único ejemplo; es editable por muestra
  ("Nombre MSP") por si no generaliza a otro tipo de muestra/protocolo;
- la versión de KB del Biotyper no viaja en el `.mzML` de VITEK, hay que completarla a
  mano en "Datos del proyecto" si se conoce.

Antes de usarlo en producción, conviene subir un lote de prueba a MicrobeNet y confirmar
que lo acepta e identifica como se espera.

Todo el procesamiento ocurre en el navegador (sin subir archivos a ningún servidor), usando
[fflate](https://github.com/101arrowz/fflate) (vendorizado en `vendor/`) para descomprimir
los arrays binarios `zlib`/`gzip` del mzML.

## `extras/tacometro.html`

Herramienta anterior del repo (un velocímetro/gauge genérico), sin relación con
bioMérieux. Se dejó archivada acá por si todavía se usa en algún lado.
