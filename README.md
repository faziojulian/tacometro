# tacometro

Herramientas web estáticas, sin backend. Todo corre en el navegador: los archivos
nunca se suben a ningún servidor.

| Página | Qué hace |
| --- | --- |
| [`index.html`](https://faziojulian.github.io/tacometro/) | **Convertidor de espectros VITEK® MS**: pasa archivos `.mzML` a un `.XML` de proyecto y a listas de picos en CSV, con vista previa del espectro. |
| [`pdf-a-excel.html`](https://faziojulian.github.io/tacometro/pdf-a-excel.html) | Convierte reportes de panel en PDF a Excel. Varios archivos a la vez. |
| [`tacometro.html`](https://faziojulian.github.io/tacometro/tacometro.html) | Tacómetro: le pasás un valor de 0 a 1 y lo muestra en la aguja. Botón para descargar la imagen como PNG. |

> Nota: el nombre del repositorio en GitHub todavía es `tacometro`. GitHub no permite
> renombrarlo por API/token de esta integración, así que hay que hacerlo a mano desde
> **Settings → General → Repository name**.

## `index.html` — conversor mzML → XML

Página principal (se sirve en la raíz de GitHub Pages). Convierte corridas de
**VITEK® MS** y **VITEK MS PRIME** en:

- una lista de picos por muestra (m/z, intensidad, y S/N + resolución estimadas desde el
  perfil), con vista previa interactiva del espectro; exportable en CSV;
- un único archivo `.xml` de **proyecto** (`<MspMatchResult>`, con un `<Analyte>` por
  muestra) con las intensidades normalizadas 0–1.

> Proyecto independiente y de código abierto, **sin afiliación ni respaldo oficial de
> bioMérieux**. VITEK® es una marca registrada de bioMérieux. Es una herramienta de
> conversión de formato, no un dispositivo de diagnóstico.

Las muestras se rotulan según su origen (**IVD**, **RUO** o **AVG**): para identificar se
recomiendan las IVD, y las demás quedan marcadas con una advertencia.

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

Usa [fflate](https://github.com/101arrowz/fflate) (vendorizado en `vendor/`) para
descomprimir los arrays binarios `zlib`/`gzip` del mzML.

## `pdf-a-excel.html`

Arrastrás uno o varios PDF de reporte de panel y se arma una tabla donde:

- **cada corrida es una fila**
- **cada target es una columna**
- el **Sample ID** del reporte se exporta como **LAB ID**

Además de los targets se extraen Run Date, Sample Type, Pouch Type, Pouch Lot,
Pouch Serial Number, Internal Process Controls, Instrument y Operator, más una
columna `Positivos` que resume los targets positivos de esa corrida.

Se descarga como `.xlsx` o `.csv`. Los archivos nunca salen de tu máquina: el
PDF se parsea localmente con pdf.js y el Excel se genera con SheetJS.

Si un panel trae targets distintos, las columnas se van agregando solas: cada
fila queda vacía en los targets que su reporte no incluye.

## `tools/build_artifact.py` — versión de un solo archivo

Genera una copia del conversor de mzML en un único `.html`, con fflate embebido, para
publicarlo donde no se pueden servir archivos aparte o para tenerlo portátil (funciona
offline con solo abrirlo):

```
python3 tools/build_artifact.py salida.html --completo
```

Al embeber la librería la aísla a propósito, para que su envoltorio UMD no se registre en
un cargador de módulos de la página anfitriona y siempre quede disponible como global; sin
eso, la app falla con `fflate is not defined` al abrir un `.mzML` comprimido con zlib.
