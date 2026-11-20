# Problema de transporte

Programa en Python puro (sin librerías externas) que resuelve el problema de
transporte en dos etapas:

1. **Solución básica factible inicial** con uno de tres métodos:
   Esquina Noroeste, Costo Mínimo o Aproximación de Vogel.
2. **Optimización** con el método **DIMO** (Distribución Modificada / MODI).

Todo el procedimiento se imprime en la terminal y se guarda en la carpeta
`resultados/` en tres formatos:

- `reporte_<metodo>.txt`: tablas en texto.
- `reporte_<metodo>.csv`: tablas para abrir en Excel o LibreOffice (separador `;`).
- `reporte_<metodo>.html`: tablas con formato para ver en el navegador.

## Uso

```bash
python3 main.py                         # menú interactivo
python3 main.py ejemplos/ejemplo1.txt   # leer datos desde archivo
```

### Formato del archivo de datos

```
oferta: 35 50 40
demanda: 45 20 30 30
costos:
8 6 10 9
9 12 13 7
14 9 16 5
```

Las líneas que empiezan con `#` se ignoran. Si el problema no está balanceado,
el programa agrega automáticamente un origen o destino ficticio con costo 0.

## Archivos

| Archivo | Contenido |
|---|---|
| `main.py` | Menú, captura de datos y flujo general |
| `balanceo.py` | Balanceo con origen/destino ficticio |
| `metodos_iniciales.py` | Esquina Noroeste, Costo Mínimo y Vogel |
| `dimo.py` | Método DIMO: multiplicadores u y v, índices, ciclo, theta |
| `utilidades.py` | Formato de tablas y guardado de reportes |
| `ejemplos/` | Problemas de prueba |

## Lectura de las tablas

Cada celda muestra `asignación [costo]`. Una celda `0 [c]` es básica con
asignación cero (solución degenerada). En las tablas de DIMO las celdas no
básicas muestran su índice `d=c_ij - u_i - v_j`; cuando todos son mayores o
iguales a cero la solución es óptima.

## Casos de prueba

Los archivos de `ejemplos/` cubren distintos tipos de problema. Se pueden correr
con `python3 main.py ejemplos/<archivo>` o capturarlos a mano con los valores
que se listan a continuación (cada línea corresponde a una pregunta del menú).
Al final el programa pregunta el método inicial; la opción `4` corre los tres.

### 1. Balanceado clásico (`ejemplo1.txt`, óptimo 1020)
Sirve para comparar los tres métodos iniciales: Noroeste da 1180, Costo Mínimo
1080 y Vogel llega directo al óptimo.
- Número de orígenes (filas): `3`
- Número de destinos (columnas): `4`
- Costos del origen O1: `8 6 10 9`
- Costos del origen O2: `9 12 13 7`
- Costos del origen O3: `14 9 16 5`
- Oferta de los 3 orígenes: `35 50 40`
- Demanda de los 4 destinos: `45 20 30 30`

### 2. Oferta mayor que la demanda (`ejemplo2_desbalanceado.txt`, óptimo 560)
Se agrega un destino ficticio. Las unidades enviadas a él no se envían realmente.
- Número de orígenes (filas): `3`
- Número de destinos (columnas): `3`
- Costos del origen O1: `4 8 8`
- Costos del origen O2: `16 24 16`
- Costos del origen O3: `8 16 24`
- Oferta de los 3 orígenes: `20 30 25`
- Demanda de los 3 destinos: `10 25 15`

### 3. Degenerado (`ejemplo3_degenerado.txt`, óptimo 435)
Con Esquina Noroeste aparece una iteración de DIMO con theta = 0 y una celda
básica con asignación cero, que se muestra como `0 [costo]`.
- Número de orígenes (filas): `3`
- Número de destinos (columnas): `4`
- Costos del origen O1: `10 2 20 11`
- Costos del origen O2: `12 7 9 20`
- Costos del origen O3: `4 14 16 18`
- Oferta de los 3 orígenes: `15 25 10`
- Demanda de los 4 destinos: `5 15 15 15`

### 4. Demanda mayor que la oferta (`ejemplo4_demanda_mayor.txt`, óptimo 205)
Se agrega un origen ficticio. El destino que recibe de él se queda sin surtir.
- Número de orígenes (filas): `2`
- Número de destinos (columnas): `3`
- Costos del origen O1: `2 3 1`
- Costos del origen O2: `5 4 8`
- Oferta de los 2 orígenes: `30 40`
- Demanda de los 3 destinos: `20 25 35`

### 5. Óptimos alternativos (`ejemplo5_optimos_alternativos.txt`, óptimo 200)
Las dos filas cuestan igual, así que hay varias soluciones óptimas. En la tabla
final aparece una celda no básica con d = 0 y el programa lo avisa.
- Número de orígenes (filas): `2`
- Número de destinos (columnas): `2`
- Costos del origen O1: `3 5`
- Costos del origen O2: `3 5`
- Oferta de los 2 orígenes: `20 30`
- Demanda de los 2 destinos: `25 25`

### 6. Ruta prohibida (`ejemplo6_ruta_prohibida.txt`, óptimo 560)
El costo 999 hace el papel de M grande. Esquina Noroeste la usa y arranca en
30260, pero DIMO la saca de la solución.
- Número de orígenes (filas): `3`
- Número de destinos (columnas): `3`
- Costos del origen O1: `5 7 999`
- Costos del origen O2: `4 6 8`
- Costos del origen O3: `9 3 6`
- Oferta de los 3 orígenes: `30 40 30`
- Demanda de los 3 destinos: `20 50 30`

### 7. Problema grande 4x5 (`ejemplo7_grande.txt`, óptimo 1460)
Desde Noroeste DIMO necesita 8 iteraciones con ciclos largos. Costo Mínimo y
Vogel ya dan el óptimo.
- Número de orígenes (filas): `4`
- Número de destinos (columnas): `5`
- Costos del origen O1: `12 7 9 15 6`
- Costos del origen O2: `8 11 13 5 10`
- Costos del origen O3: `14 9 6 12 11`
- Costos del origen O4: `7 13 10 8 14`
- Oferta de los 4 orígenes: `40 60 50 50`
- Demanda de los 5 destinos: `30 50 40 40 40`

### 8. Costos decimales (`ejemplo8_decimales.txt`, óptimo 479.50)
Comprueba que el programa acepta decimales y los muestra con dos cifras.
- Número de orígenes (filas): `2`
- Número de destinos (columnas): `3`
- Costos del origen O1: `1.5 2.25 3.1`
- Costos del origen O2: `2.8 1.75 2.4`
- Oferta de los 2 orígenes: `100 150`
- Demanda de los 3 destinos: `80 90 80`

Orden sugerido para una exposición: 1 para comparar métodos, 2 y 4 para el
balanceo, 3 para degeneración, 5 para óptimos alternativos y 7 para ver muchas
iteraciones.
