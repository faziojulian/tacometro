# tacometro

Dos herramientas web estáticas, sin backend. Todo corre en el navegador.

| Página | Qué hace |
| --- | --- |
| [`tacometro.html`](https://faziojulian.github.io/tacometro/tacometro.html) | Tacómetro: le pasás un valor de 0 a 1 y lo muestra en la aguja. Botón para descargar la imagen como PNG. |
| [`pdf-a-excel.html`](https://faziojulian.github.io/tacometro/pdf-a-excel.html) | Convierte reportes de panel en PDF a Excel. Varios archivos a la vez. |

## pdf-a-excel

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
