"""Método DIMO (Distribución Modificada, también llamado MODI o u-v).

Parte de una solución básica factible y la mejora hasta llegar al óptimo.
"""

from utilidades import fmt, es_cero, tabla_transporte, costo_total


def calcular_uv(costos, basicas, m, n):
    """Resuelve u_i + v_j = c_ij para las celdas básicas, con u_0 = 0."""
    u = [None] * m
    v = [None] * n
    u[0] = 0
    cambio = True
    while cambio:
        cambio = False
        for (i, j) in basicas:
            if u[i] is not None and v[j] is None:
                v[j] = costos[i][j] - u[i]
                cambio = True
            elif v[j] is not None and u[i] is None:
                u[i] = costos[i][j] - v[j]
                cambio = True
    return u, v


def encontrar_ciclo(basicas, inicio):
    """Busca el ciclo cerrado que parte de 'inicio' y pasa solo por celdas básicas.

    Se alternan movimientos por fila y por columna. Devuelve la lista de celdas
    del ciclo (la primera es 'inicio') o None si no existe.
    """
    candidatas = sorted(basicas)

    def dfs(camino, por_fila):
        actual = camino[-1]
        for c in candidatas:
            if c in camino:
                continue
            if por_fila and c[0] != actual[0]:
                continue
            if not por_fila and c[1] != actual[1]:
                continue
            cierra = (por_fila and c[1] == inicio[1]) or (not por_fila and c[0] == inicio[0])
            if cierra and len(camino) >= 3:
                return camino + [c]
            resultado = dfs(camino + [c], not por_fila)
            if resultado:
                return resultado
        return None

    return dfs([inicio], True)


def completar_base(costos, asignacion, basicas, m, n, nombres_f, nombres_c, reporte):
    """Si hay menos de m+n-1 básicas (degeneración), agrega celdas con asignación 0.

    Se elige la celda no básica de menor costo que no forme ciclo con las básicas.
    """
    requeridas = m + n - 1
    while len(basicas) < requeridas:
        opciones = []
        for i in range(m):
            for j in range(n):
                if (i, j) in basicas:
                    continue
                if encontrar_ciclo(basicas | {(i, j)}, (i, j)) is None:
                    opciones.append((costos[i][j], i, j))
        if not opciones:
            raise RuntimeError("No fue posible completar la base.")
        _, i, j = min(opciones)
        basicas.add((i, j))
        asignacion[i][j] = 0
        reporte.texto(f"Solución degenerada: se agrega la celda ({nombres_f[i]}, {nombres_c[j]}) "
                      f"como básica con asignación 0 (hay {len(basicas)} de {requeridas}).")


def dimo(costos, asignacion, basicas, oferta, demanda, nombres_f, nombres_c, reporte, max_iter=200):
    m, n = len(costos), len(costos[0])
    asignacion = [list(f) for f in asignacion]
    basicas = set(basicas)

    reporte.texto("\n=== Optimización: Método DIMO ===")
    completar_base(costos, asignacion, basicas, m, n, nombres_f, nombres_c, reporte)

    iteracion = 0
    while True:
        iteracion += 1
        if iteracion > max_iter:
            raise RuntimeError("Se superó el máximo de iteraciones.")

        u, v = calcular_uv(costos, basicas, m, n)
        if None in u or None in v:
            raise RuntimeError("La base no está conectada; no se pueden calcular u y v.")

        indices = [[None] * n for _ in range(m)]
        minimo, entrante = None, None
        for i in range(m):
            for j in range(n):
                if (i, j) in basicas:
                    continue
                d = costos[i][j] - u[i] - v[j]
                indices[i][j] = d
                if minimo is None or d < minimo:
                    minimo, entrante = d, (i, j)

        reporte.texto(f"\n--- Iteración {iteracion} ---")
        reporte.texto("Multiplicadores (u_0 = 0): "
                      + ", ".join(f"u({nombres_f[i]})={fmt(u[i])}" for i in range(m)) + "; "
                      + ", ".join(f"v({nombres_c[j]})={fmt(v[j])}" for j in range(n)))
        enc, fil = tabla_transporte(costos, asignacion, basicas, oferta, demanda,
                                    nombres_f, nombres_c, u=u, v=v, indices=indices)
        reporte.tabla(f"Iteración {iteracion}: asignaciones e índices d_ij = c_ij - u_i - v_j:", enc, fil)
        reporte.texto(f"Costo actual: {fmt(costo_total(costos, asignacion))}")

        if minimo is None or minimo >= -1e-9:
            reporte.texto("Todos los índices d_ij son mayores o iguales a cero: la solución es ÓPTIMA.")
            break

        i0, j0 = entrante
        reporte.texto(f"Índice más negativo: d={fmt(minimo)} en ({nombres_f[i0]}, {nombres_c[j0]}). "
                      f"Esa celda entra a la base.")

        ciclo = encontrar_ciclo(basicas | {entrante}, entrante)
        if ciclo is None:
            raise RuntimeError("No se encontró un ciclo cerrado.")

        signos = ["+" if k % 2 == 0 else "-" for k in range(len(ciclo))]
        reporte.texto("Ciclo cerrado: " + " -> ".join(
            f"{s}({nombres_f[i]}, {nombres_c[j]})" for s, (i, j) in zip(signos, ciclo)))

        negativas = ciclo[1::2]
        theta = min(asignacion[i][j] for (i, j) in negativas)
        saliente = next((i, j) for (i, j) in negativas if es_cero(asignacion[i][j] - theta))
        reporte.texto(f"theta = mínimo de las celdas con signo '-' = {fmt(theta)}. "
                      f"Sale de la base ({nombres_f[saliente[0]]}, {nombres_c[saliente[1]]}).")

        for k, (i, j) in enumerate(ciclo):
            if k % 2 == 0:
                asignacion[i][j] += theta
            else:
                asignacion[i][j] -= theta
                if es_cero(asignacion[i][j]):
                    asignacion[i][j] = 0
        basicas.remove(saliente)
        basicas.add(entrante)

    # ------------------------------------------------------------ resultado
    reporte.texto("\n=== Solución óptima ===")
    enc, fil = tabla_transporte(costos, asignacion, basicas, oferta, demanda, nombres_f, nombres_c)
    reporte.tabla("Tabla óptima:", enc, fil)
    reporte.texto("Envíos:")
    for i in range(m):
        for j in range(n):
            if (i, j) in basicas and not es_cero(asignacion[i][j]):
                nota = "  (ficticio: no se envía realmente)" if "Ficticio" in (nombres_f[i], nombres_c[j]) else ""
                reporte.texto(f"  {nombres_f[i]} -> {nombres_c[j]}: {fmt(asignacion[i][j])} unidades "
                              f"x costo {fmt(costos[i][j])} = {fmt(asignacion[i][j] * costos[i][j])}{nota}")
    reporte.texto(f"COSTO MÍNIMO TOTAL: {fmt(costo_total(costos, asignacion))}")

    alternativas = [(i, j) for i in range(m) for j in range(n)
                    if (i, j) not in basicas and es_cero(indices[i][j])]
    if alternativas:
        reporte.texto("Existen soluciones óptimas alternativas: hay índices d_ij = 0 en "
                      + ", ".join(f"({nombres_f[i]}, {nombres_c[j]})" for i, j in alternativas) + ".")
    return asignacion, basicas
