# tacometro

Herramientas web estáticas, sin backend. Todo corre en el navegador: los archivos
nunca se suben a ningún servidor.

| Página | Qué hace |
| --- | --- |
| [`index.html`](https://faziojulian.github.io/tacometro/) | **Convertidor de espectros VITEK® MS**: pasa archivos `.mzML` a un `.XML` de proyecto y a listas de picos en CSV o TXT, con vista previa del espectro. |
| [`pdf-a-excel.html`](https://faziojulian.github.io/tacometro/pdf-a-excel.html) | Convierte reportes de panel en PDF a Excel. Varios archivos a la vez. |
| [`tacometro.html`](https://faziojulian.github.io/tacometro/tacometro.html) | Tacómetro: le pasás un valor de 0 a 1 y lo muestra en la aguja. Botón para descargar la imagen como PNG. |

> Nota: el nombre del repositorio en GitHub todavía es `tacometro`. GitHub no permite
> renombrarlo por API/token de esta integración, así que hay que hacerlo a mano desde
> **Settings → General → Repository name**.

## `index.html` — conversor mzML → XML

Página principal (se sirve en la raíz de GitHub Pages). Convierte corridas de
**VITEK® MS** y **VITEK MS PRIME** en:

- una lista de picos por muestra (m/z, intensidad, y S/N + resolución estimadas desde el
  perfil), con vista previa interactiva del espectro; exportable en **CSV** (con encabezado
  y las columnas de S/N y resolución) o en **TXT** (dos columnas, m/z e intensidad separadas
  por tabulación y sin encabezado, que es lo que leen mMass, MALDIquant y similares), por
  muestra o todas juntas en un `.zip`;
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
  generaliza a otro tipo de muestra/protocolo. El modelo del equipo **no se adivina**: sale
  del cvParam de modelo (`BM:1001080`) o, si no está, del nombre de instrumento del propio
  archivo (`BM:1001071`); si el archivo no declara ninguno, ese segmento se omite en vez de
  afirmar un modelo que no es. La abreviatura exacta para VITEK MS Legacy está confirmada
  contra pipelines de terceros, no contra un archivo Legacy real;
- la versión de KB no viaja en el `.mzML` de VITEK, hay que completarla a mano en "Datos
  del proyecto" si se conoce;
- S/N y resolución son estimaciones calculadas desde el perfil exportado (línea de base y
  ruido locales, FWHM), no los valores exactos del software del equipo.

Antes de usarlo en producción, conviene procesar un lote de prueba y verificar que el
archivo se acepta e identifica como se espera.

**`index.html` es un único archivo autocontenido**: trae
[fflate](https://github.com/101arrowz/fflate) (MIT) embebido para descomprimir los
arrays binarios `zlib`/`gzip` del mzML y armar los `.zip`. Se puede copiar solo a
cualquier lado y funciona offline con abrirlo; no necesita la carpeta `vendor/` al
lado, que queda en el repo como origen de la copia y para la licencia.

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

## `tools/build_artifact.py` — versión para Artifact

Para tener el conversor portátil alcanza con copiar `index.html`: ya es un solo archivo.
Este script existe sólo para el formato de Artifact de claude.ai, que espera el contenido
**sin** el envoltorio del documento (lo agrega el anfitrión):

```
python3 tools/build_artifact.py salida.html              # cuerpo para Artifact
python3 tools/build_artifact.py salida.html --completo   # documento entero
```

En `index.html`, fflate va envuelta en una función que declara `define`, `module` y
`exports` como variables locales vacías. Sin ese aislamiento, en una página anfitriona con
cargador de módulos el UMD se registra ahí, nunca crea la global `fflate`, y la app falla
con `fflate is not defined` al abrir un `.mzML` comprimido con zlib o al armar un `.zip`.
