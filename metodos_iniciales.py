"""Métodos para obtener una solución básica factible inicial.

Los tres métodos comparten el mismo esquema: elegir una celda, asignar el
mínimo entre oferta y demanda restantes y tachar la fila o columna agotada.
Solo cambia la regla para elegir la celda (el "selector").
"""

from utilidades import fmt, es_cero, tabla_transporte, costo_total


def _resolver(costos, oferta, demanda, nombres_f, nombres_c, selector, nombre, reporte):
    m, n = len(costos), len(costos[0]) # m-filas, n-columnas
    of = list(oferta)
    de = list(demanda) #copias de la oferta y demanda para ir restando
    asignacion = [[0] * n for _ in range(m)] #creación de la tabla de asignación, guarda las cantidades asignadas
    basicas = set() #conjunto vacio donde se anotan las celdas usadas
    filas = list(range(m))
    cols = list(range(n)) #listas de filas y columnas disponibles (no agotadas)
    paso = 0 

    reporte.texto(f"\n=== Solución inicial: {nombre} ===") 
    while filas and cols: #codicional si hay filas y columnas disponibles
        paso += 1
        i, j, explicacion = selector(costos, of, de, filas, cols, nombres_f, nombres_c) #aqui la funcion selector elije la celda para usar
        x = min(of[i], de[j]) #cantidad a asignar, el minimo entre oferta y demanda
        asignacion[i][j] = x #se anota la cantidad en la celda de la tabla de asignacion
        basicas.add((i, j)) #se marva la celda como usada, basica
        of[i] -= x 
        de[j] -= x #resta la cantidad asignada de la oferta y demanda
        reporte.texto(f"Paso {paso}: {explicacion} Se asigna {fmt(x)} en "
                      f"({nombres_f[i]}, {nombres_c[j]}).")

        if es_cero(of[i]) and es_cero(de[j]): #si la oferta y la demanda de la celda son cero
            # Se agotan ambas a la vez: solo se tacha una línea para conservar
            # m+n-1 celdas básicas (la otra recibirá una asignación 0 después).
            if len(filas) > 1: #si hay más de una fila disponible
                filas.remove(i)
                reporte.texto(f"        Se agotan {nombres_f[i]} y {nombres_c[j]} a la vez; "
                              f"se tacha solo {nombres_f[i]} (la columna queda con demanda 0).")
            elif len(cols) > 1: #si hay más de una columna disponible
                cols.remove(j)
                reporte.texto(f"        Se agotan {nombres_f[i]} y {nombres_c[j]} a la vez; "
                              f"se tacha solo {nombres_c[j]} (la fila queda con oferta 0).")
            else: #si solo queda una fila y una columna, se tacha cualquiera de las dos
                filas.remove(i)
                cols.remove(j)
        elif es_cero(of[i]): #si la oferta es cero
            filas.remove(i)
            reporte.texto(f"        Se tacha {nombres_f[i]} (oferta agotada).")
        else: #si la demanda es cero
            cols.remove(j)
            reporte.texto(f"        Se tacha {nombres_c[j]} (demanda satisfecha).")

        enc, fil = tabla_transporte(costos, asignacion, basicas, of, de, nombres_f, nombres_c)
        reporte.tabla(f"Tabla tras el paso {paso} (oferta y demanda restantes):", enc, fil) #armma la tabla actual

    reporte.texto(f"Celdas básicas obtenidas: {len(basicas)} (se requieren m+n-1 = {m + n - 1}).") #se verifica que se tengan bien las rutas
    enc, fil = tabla_transporte(costos, asignacion, basicas, oferta, demanda, nombres_f, nombres_c)
    reporte.tabla(f"Solución inicial por {nombre}:", enc, fil) #muestra la tabla final de la solucion inicial
    reporte.texto(f"Costo total de la solución inicial: {fmt(costo_total(costos, asignacion))}") #calcula el costo total suma de asignaciones * costo de la celda
    return asignacion, basicas


# ---------------------------------------------------------------- selectores

def _selector_noroeste(costos, of, de, filas, cols, nombres_f, nombres_c):
    i, j = min(filas), min(cols)
    return i, j, f"Esquina noroeste disponible: ({nombres_f[i]}, {nombres_c[j]})."
#selecciona la celda superior izquierda disponible 


def _selector_costo_minimo(costos, of, de, filas, cols, nombres_f, nombres_c):
    mejor = None #
    for i in filas:
        for j in cols:
            if mejor is None or costos[i][j] < costos[mejor[0]][mejor[1]]:
                mejor = (i, j)
    i, j = mejor
    return i, j, f"Menor costo disponible: {fmt(costos[i][j])} en ({nombres_f[i]}, {nombres_c[j]})."
#selecciona la celda con el menor costo disponible


def _penalizacion(valores):
    """Diferencia entre los dos menores costos (o el único costo si queda uno)."""
    if len(valores) == 1:
        return valores[0]
    ordenados = sorted(valores)
    return ordenados[1] - ordenados[0]
#Calcula la penalización de una fila o columna, que es la diferencia entre los dos menores costos.


def _selector_vogel(costos, of, de, filas, cols, nombres_f, nombres_c):
    pen_f = {i: _penalizacion([costos[i][j] for j in cols]) for i in filas}
    pen_c = {j: _penalizacion([costos[i][j] for i in filas]) for j in cols}

    mejor_pen, tipo, idx = None, None, None
    for i in filas:
        if mejor_pen is None or pen_f[i] > mejor_pen:
            mejor_pen, tipo, idx = pen_f[i], "fila", i
    for j in cols:
        if pen_c[j] > mejor_pen:
            mejor_pen, tipo, idx = pen_c[j], "columna", j
    #busca la mayor penalización entre filas y columnas, y guarda el tipo (fila o columna) y el índice correspondiente

    if tipo == "fila":
        i = idx
        j = min(cols, key=lambda jj: (costos[i][jj], jj))
        donde = nombres_f[i]
    else:
        j = idx
        i = min(filas, key=lambda ii: (costos[ii][j], ii))
        donde = nombres_c[j]

    txt_f = ", ".join(f"{nombres_f[i2]}={fmt(pen_f[i2])}" for i2 in filas)
    txt_c = ", ".join(f"{nombres_c[j2]}={fmt(pen_c[j2])}" for j2 in cols)
    explicacion = (f"Penalizaciones -> filas: {txt_f}; columnas: {txt_c}. "
                   f"Mayor penalización: {donde} ({fmt(mejor_pen)}); "
                   f"su menor costo es {fmt(costos[i][j])}.")
    return i, j, explicacion


# ---------------------------------------------------------- funciones públicas

def esquina_noroeste(costos, oferta, demanda, nombres_f, nombres_c, reporte):
    return _resolver(costos, oferta, demanda, nombres_f, nombres_c,
                     _selector_noroeste, "Esquina Noroeste", reporte)


def costo_minimo(costos, oferta, demanda, nombres_f, nombres_c, reporte):
    return _resolver(costos, oferta, demanda, nombres_f, nombres_c,
                     _selector_costo_minimo, "Costo Mínimo", reporte)


def vogel(costos, oferta, demanda, nombres_f, nombres_c, reporte):
    return _resolver(costos, oferta, demanda, nombres_f, nombres_c,
                     _selector_vogel, "Aproximación de Vogel", reporte)

#las 3 llaman a resolver con el selector de cada metodo y pasa los parametros


METODOS = {
    "1": ("Esquina Noroeste", esquina_noroeste, "noroeste"),
    "2": ("Costo Mínimo", costo_minimo, "costo_minimo"),
    "3": ("Aproximación de Vogel", vogel, "vogel"),
}
