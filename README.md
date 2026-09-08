# Convertidor de espectros VITEK® MS

Convierte archivos `.mzML` de corridas **VITEK® MS** y **VITEK MS PRIME** a un archivo
`.XML` de proyecto (formato `MspMatchResult`) y a listas de picos en CSV, con vista previa
del espectro. Todo corre en el navegador: los archivos nunca se suben a ningún servidor.

> Proyecto independiente y de código abierto, **sin afiliación ni respaldo oficial de
> bioMérieux**. VITEK® es una marca registrada de bioMérieux.

> Nota: el nombre del repositorio en GitHub todavía es `tacometro`. GitHub no permite
> renombrarlo por API/token de esta integración, así que hay que hacerlo a mano desde
> **Settings → General → Repository name**.

## `index.html` — conversor mzML → XML

`index.html` es la página principal (se sirve en la raíz de GitHub Pages). Convierte uno o
varios archivos `.mzML` en:

- una lista de picos por muestra (m/z, intensidad, y S/N + resolución estimadas desde el
  perfil), con vista previa interactiva del espectro; exportable en CSV;
- un único archivo `.xml` de **proyecto** (`<MspMatchResult>`, con un `<Analyte>` por
  muestra) con las intensidades normalizadas 0–1.

**Esquema del XML:** la estructura (`MspMatchResult` > `ProjectInfo` + `Analytes` >
`Analyte` > `Peaklist` > `Peaks` > `Peak`) se tomó de archivos `.xml` reales, no es una
suposición; se corroboró de forma independiente contra tres fuentes. Puntos que son
best-effort y conviene revisar:

- el nombre de cada `Analyte` (`name`/`externId`) se reconstruye combinando campos del
  `.mzML` según el patrón observado; es editable por muestra ("Nombre MSP") por si no
  generaliza a otro tipo de muestra/protocolo;
- la versión de KB no viaja en el `.mzML` de VITEK, hay que completarla a mano en "Datos
  del proyecto" si se conoce;
- S/N y resolución son estimaciones calculadas desde el perfil exportado (línea de base y
  ruido locales, FWHM), no los valores exactos del software del equipo.

Antes de usarlo en producción, conviene procesar un lote de prueba y verificar que el
archivo se acepta e identifica como se espera.

Todo el procesamiento ocurre en el navegador (sin subir archivos a ningún servidor), usando
[fflate](https://github.com/101arrowz/fflate) (vendorizado en `vendor/`) para descomprimir
los arrays binarios `zlib`/`gzip` del mzML.

## `tools/build_artifact.py` — versión de un solo archivo

Genera una copia de la app en un único `.html`, con fflate embebido, para publicarla donde
no se pueden servir archivos aparte o para tenerla portátil (funciona offline con solo
abrirla):

```
python3 tools/build_artifact.py salida.html --completo
```

Al embeber la librería la aísla a propósito, para que su envoltorio UMD no se registre en
un cargador de módulos de la página anfitriona y siempre quede disponible como global; sin
eso, la app falla con `fflate is not defined` al abrir un `.mzML` comprimido con zlib.

## `extras/tacometro.html`

Herramienta anterior del repo (un velocímetro/gauge genérico), sin relación con este
conversor. Se dejó archivada acá por si todavía se usa en algún lado.
