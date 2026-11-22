"""Método del Banquillo (Stepping Stone o Piedra de Paso).

Parte de una solución básica factible y la mejora hasta llegar al óptimo.
Para cada celda no básica se traza su ciclo cerrado sobre celdas básicas y se
calcula su costo marginal sumando los costos con signos alternados (+, -, +, ...).
Si algún costo marginal es negativo, la celda con el más negativo entra a la base.
"""

from dimo import encontrar_ciclo, completar_base
from utilidades import fmt, es_cero, tabla_transporte, costo_total


def evaluar_celda(costos, basicas, celda):
    """Devuelve (costo_marginal, ciclo) de una celda no básica."""
    ciclo = encontrar_ciclo(basicas | {celda}, celda)
    if ciclo is None:
        raise RuntimeError("No se encontró un ciclo cerrado.")
    costo = sum(costos[i][j] if k % 2 == 0 else -costos[i][j]
                for k, (i, j) in enumerate(ciclo))
    return costo, ciclo


def _texto_ciclo(costos, ciclo, nombres_f, nombres_c):
    return " ".join(
        f"{'+' if k % 2 == 0 else '-'}{fmt(costos[i][j])}({nombres_f[i]},{nombres_c[j]})"
        for k, (i, j) in enumerate(ciclo))


def banquillo(costos, asignacion, basicas, oferta, demanda, nombres_f, nombres_c, reporte, max_iter=200):
    m, n = len(costos), len(costos[0])
    asignacion = [list(f) for f in asignacion]
    basicas = set(basicas)

    reporte.texto("\n=== Optimización: Método del Banquillo (Stepping Stone) ===")
    completar_base(costos, asignacion, basicas, m, n, nombres_f, nombres_c, reporte)

    iteracion = 0
    while True:
        iteracion += 1
        if iteracion > max_iter:
            raise RuntimeError("Se superó el máximo de iteraciones.")

        reporte.texto(f"\n--- Iteración {iteracion} ---")
        reporte.texto("Evaluación de las celdas no básicas (ciclo cerrado y costo marginal):")

        indices = [[None] * n for _ in range(m)]
        ciclos = {}
        minimo, entrante = None, None
        for i in range(m):
            for j in range(n):
                if (i, j) in basicas:
                    continue
                d, ciclo = evaluar_celda(costos, basicas, (i, j))
                indices[i][j] = d
                ciclos[(i, j)] = ciclo
                reporte.texto(f"  ({nombres_f[i]}, {nombres_c[j]}): "
                              f"{_texto_ciclo(costos, ciclo, nombres_f, nombres_c)} = {fmt(d)}")
                if minimo is None or d < minimo:
                    minimo, entrante = d, (i, j)

        enc, fil = tabla_transporte(costos, asignacion, basicas, oferta, demanda,
                                    nombres_f, nombres_c, indices=indices)
        reporte.tabla(f"Iteración {iteracion}: asignaciones y costos marginales d de las celdas no básicas:",
                      enc, fil)
        reporte.texto(f"Costo actual: {fmt(costo_total(costos, asignacion))}")

        if minimo is None or minimo >= -1e-9:
            reporte.texto("Todos los costos marginales son mayores o iguales a cero: la solución es ÓPTIMA.")
            break

        i0, j0 = entrante
        ciclo = ciclos[entrante]
        reporte.texto(f"Costo marginal más negativo: {fmt(minimo)} en ({nombres_f[i0]}, {nombres_c[j0]}). "
                      f"Esa celda entra a la base.")
        reporte.texto("Ciclo cerrado: " + " -> ".join(
            f"{'+' if k % 2 == 0 else '-'}({nombres_f[i]}, {nombres_c[j]})" for k, (i, j) in enumerate(ciclo)))

        negativas = ciclo[1::2]
        theta = min(asignacion[i][j] for (i, j) in negativas)
        saliente = next((i, j) for (i, j) in negativas if es_cero(asignacion[i][j] - theta))
        reporte.texto(f"theta = mínimo de las celdas con signo '-' = {fmt(theta)}. "
                      f"Sale de la base ({nombres_f[saliente[0]]}, {nombres_c[saliente[1]]}). "
                      f"El costo baja en {fmt(-minimo * theta)}.")

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
        reporte.texto("Existen soluciones óptimas alternativas: hay costos marginales = 0 en "
                      + ", ".join(f"({nombres_f[i]}, {nombres_c[j]})" for i, j in alternativas) + ".")
    return asignacion, basicas
