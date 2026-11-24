
"""
Método DIMO (Distribución Modificada, también llamado MODI o u-v).

Parte de una solución básica factible y la mejora hasta llegar al óptimo.
"""

from utilidades import fmt, es_cero, tabla_transporte, costo_total


# Calcula los multiplicadores de filas y columnas.
def calcular_uv(costos, basicas, m, n):
    """Resuelve u_i + v_j = c_ij para las celdas básicas."""

    u = [None] * m
    v = [None] * n

    u[0] = 0  # Valor inicial para calcular los demás multiplicadores

    cambio = True
    while cambio:
        cambio = False

        for (i, j) in basicas:

            # Calcula V cuando ya se conoce U.
            if u[i] is not None and v[j] is None:
                v[j] = costos[i][j] - u[i]
                cambio = True

            # Calcula U cuando ya se conoce V.
            elif v[j] is not None and u[i] is None:
                u[i] = costos[i][j] - v[j]
                cambio = True

    return u, v


# Busca un ciclo cerrado para realizar la redistribución.
def encontrar_ciclo(basicas, inicio):
    """Busca el ciclo alternando movimientos por filas y columnas."""

    candidatas = sorted(basicas)

    def dfs(camino, por_fila):
        actual = camino[-1]

        for c in candidatas:

            if c in camino:
                continue

            # Verifica que el movimiento siga por la misma fila o columna.
            if por_fila and c[0] != actual[0]:
                continue
            if not por_fila and c[1] != actual[1]:
                continue

            # Comprueba si el recorrido puede regresar al inicio.
            cierra = (
                (por_fila and c[1] == inicio[1])
                or (not por_fila and c[0] == inicio[0])
            )

            if cierra and len(camino) >= 3:
                return camino + [c]

            # Continúa la búsqueda cambiando de dirección.
            resultado = dfs(camino + [c], not por_fila)

            if resultado:
                return resultado

        return None

    return dfs([inicio], True)


# Completa las celdas básicas cuando existe degeneración.
def completar_base(
    costos, asignacion, basicas, m, n,
    nombres_f, nombres_c, reporte
):
    """Agrega celdas con asignación cero hasta completar la base."""

    requeridas = m + n - 1

    while len(basicas) < requeridas:
        opciones = []

        for i in range(m):
            for j in range(n):

                if (i, j) in basicas:
                    continue

                # Evita agregar celdas que formen ciclos.
                if encontrar_ciclo(basicas | {(i, j)}, (i, j)) is None:
                    opciones.append((costos[i][j], i, j))

        if not opciones:
            raise RuntimeError("No fue posible completar la base.")

        # Selecciona la celda disponible de menor costo.
        _, i, j = min(opciones)

        basicas.add((i, j))
        asignacion[i][j] = 0

        reporte.texto(
            f"Solución degenerada: se agrega la celda "
            f"({nombres_f[i]}, {nombres_c[j]}) "
            f"como básica con asignación 0 "
            f"(hay {len(basicas)} de {requeridas})."
        )


# Ejecuta el proceso de optimización DIMO.
def dimo(
    costos, asignacion, basicas, oferta, demanda,
    nombres_f, nombres_c, reporte, max_iter=200
):

    m, n = len(costos), len(costos[0])

    asignacion = [list(f) for f in asignacion]
    basicas = set(basicas)

    reporte.texto("\n=== Optimización: Método DIMO ===")

    # Verifica que la base tenga la cantidad necesaria de celdas.
    completar_base(
        costos, asignacion, basicas, m, n,
        nombres_f, nombres_c, reporte
    )

    iteracion = 0

    while True:
        iteracion += 1

        if iteracion > max_iter:
            raise RuntimeError("Se superó el máximo de iteraciones.")

        # Calcula los multiplicadores U y V.
        u, v = calcular_uv(costos, basicas, m, n)

        if None in u or None in v:
            raise RuntimeError(
                "La base no está conectada; no se pueden calcular u y v."
            )

        # Calcula los índices de mejora de las celdas no básicas.
        indices = [[None] * n for _ in range(m)]

        minimo, entrante = None, None

        for i in range(m):
            for j in range(n):

                if (i, j) in basicas:
                    continue

                # Índice de mejora: costo - U - V.
                d = costos[i][j] - u[i] - v[j]
                indices[i][j] = d

                # Guarda el índice más negativo.
                if minimo is None or d < minimo:
                    minimo, entrante = d, (i, j)

        reporte.texto(f"\n--- Iteración {iteracion} ---")

        reporte.texto(
            "Multiplicadores (u_0 = 0): "
            + ", ".join(
                f"u({nombres_f[i]})={fmt(u[i])}" for i in range(m)
            )
            + "; "
            + ", ".join(
                f"v({nombres_c[j]})={fmt(v[j])}" for j in range(n)
            )
        )

        enc, fil = tabla_transporte(
            costos, asignacion, basicas, oferta, demanda,
            nombres_f, nombres_c, u=u, v=v, indices=indices
        )

        reporte.tabla(
            f"Iteración {iteracion}: asignaciones e índices "
            f"d_ij = c_ij - u_i - v_j:",
            enc, fil
        )

        reporte.texto(
            f"Costo actual: {fmt(costo_total(costos, asignacion))}"
        )

        # Si todos los índices son no negativos, la solución es óptima.
        if minimo is None or minimo >= -1e-9:
            reporte.texto(
                "Todos los índices d_ij son mayores o iguales a cero: "
                "la solución es ÓPTIMA."
            )
            break

        # Selecciona la celda con el índice más negativo.
        i0, j0 = entrante

        reporte.texto(
            f"Índice más negativo: d={fmt(minimo)} en "
            f"({nombres_f[i0]}, {nombres_c[j0]}). "
            f"Esa celda entra a la base."
        )

        # Encuentra el ciclo cerrado que incluye la nueva celda.
        ciclo = encontrar_ciclo(basicas | {entrante}, entrante)

        if ciclo is None:
            raise RuntimeError("No se encontró un ciclo cerrado.")

        # Asigna signos alternados a las celdas del ciclo.
        signos = ["+" if k % 2 == 0 else "-" for k in range(len(ciclo))]

        reporte.texto(
            "Ciclo cerrado: "
            + " -> ".join(
                f"{s}({nombres_f[i]}, {nombres_c[j]})"
                for s, (i, j) in zip(signos, ciclo)
            )
        )

        # Calcula theta con la menor asignación de las celdas negativas.
        negativas = ciclo[1::2]
        theta = min(asignacion[i][j] for (i, j) in negativas)

        # Identifica la celda negativa que saldrá de la base.
        saliente = next(
            (i, j)
            for (i, j) in negativas
            if es_cero(asignacion[i][j] - theta)
        )

        reporte.texto(
            f"theta = mínimo de las celdas con signo '-' = "
            f"{fmt(theta)}. Sale de la base "
            f"({nombres_f[saliente[0]]}, {nombres_c[saliente[1]]})."
        )

        # Actualiza las asignaciones según los signos del ciclo.
        for k, (i, j) in enumerate(ciclo):

            if k % 2 == 0:
                asignacion[i][j] += theta
            else:
                asignacion[i][j] -= theta

                if es_cero(asignacion[i][j]):
                    asignacion[i][j] = 0

        # Actualiza las celdas que forman parte de la base.
        basicas.remove(saliente)
        basicas.add(entrante)

    # Muestra la solución obtenida.
    reporte.texto("\n=== Solución óptima ===")

    enc, fil = tabla_transporte(
        costos, asignacion, basicas,
        oferta, demanda, nombres_f, nombres_c
    )

    reporte.tabla("Tabla óptima:", enc, fil)

    reporte.texto("Envíos:")

    for i in range(m):
        for j in range(n):

            if (i, j) in basicas and not es_cero(asignacion[i][j]):

                nota = (
                    "  (ficticio: no se envía realmente)"
                    if "Ficticio" in (nombres_f[i], nombres_c[j])
                    else ""
                )

                reporte.texto(
                    f"  {nombres_f[i]} -> {nombres_c[j]}: "
                    f"{fmt(asignacion[i][j])} unidades "
                    f"x costo {fmt(costos[i][j])} = "
                    f"{fmt(asignacion[i][j] * costos[i][j])}{nota}"
                )

    # Calcula el costo mínimo de la distribución.
    reporte.texto(
        f"COSTO MÍNIMO TOTAL: {fmt(costo_total(costos, asignacion))}"
    )

    # Busca celdas no básicas con índice cero.
    alternativas = [
        (i, j)
        for i in range(m)
        for j in range(n)
        if (i, j) not in basicas and es_cero(indices[i][j])
    ]

    if alternativas:
        reporte.texto(
            "Existen soluciones óptimas alternativas: hay índices "
            "d_ij = 0 en "
            + ", ".join(
                f"({nombres_f[i]}, {nombres_c[j]})"
                for i, j in alternativas
            )
            + "."
        )

    return asignacion, basicas, iteracion
