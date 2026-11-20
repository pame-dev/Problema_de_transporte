"""Funciones de apoyo: formato de números, tablas y generación de reportes."""

import csv
import html
import os

TOLERANCIA = 1e-9


def es_cero(x):
    return abs(x) < TOLERANCIA


def fmt(x):
    """Formatea un número: entero si lo es, dos decimales si no."""
    if x is None:
        return "-"
    x = float(x)
    if x.is_integer():
        return str(int(x))
    return f"{x:.2f}"


def costo_total(costos, asignacion):
    return sum(
        costos[i][j] * asignacion[i][j]
        for i in range(len(costos))
        for j in range(len(costos[0]))
    )


def tabla_transporte(costos, asignacion, basicas, oferta, demanda,
                     nombres_f, nombres_c, u=None, v=None, indices=None):
    """Construye (encabezados, filas) de una tabla de transporte.

    Cada celda muestra 'asignación [costo]' si es básica. Si no es básica
    muestra '- [costo]' o, cuando se pasan los índices d_ij, 'd=valor [costo]'.
    Con u y v se agregan la columna u y la fila v.
    """
    encabezados = [""] + list(nombres_c) + ["Oferta"]
    if u is not None:
        encabezados.append("u")
    filas = []
    for i, nf in enumerate(nombres_f):
        fila = [nf]
        for j in range(len(nombres_c)):
            c = fmt(costos[i][j])
            if (i, j) in basicas:
                fila.append(f"{fmt(asignacion[i][j])} [{c}]")
            elif indices is not None:
                fila.append(f"d={fmt(indices[i][j])} [{c}]")
            else:
                fila.append(f"- [{c}]")
        fila.append(fmt(oferta[i]))
        if u is not None:
            fila.append(fmt(u[i]))
        filas.append(fila)
    ultima = ["Demanda"] + [fmt(d) for d in demanda] + [fmt(sum(demanda))]
    if u is not None:
        ultima.append("")
    filas.append(ultima)
    if v is not None:
        filas.append(["v"] + [fmt(x) for x in v] + ["", ""])
    return encabezados, filas


def formatear_tabla(encabezados, filas):
    """Devuelve la tabla como texto alineado para la terminal."""
    columnas = len(encabezados)
    anchos = [len(str(encabezados[k])) for k in range(columnas)]
    for fila in filas:
        for k in range(columnas):
            anchos[k] = max(anchos[k], len(str(fila[k])))

    def linea(celdas):
        return "| " + " | ".join(str(celdas[k]).rjust(anchos[k]) for k in range(columnas)) + " |"

    separador = "+" + "+".join("-" * (a + 2) for a in anchos) + "+"
    salida = [separador, linea(encabezados), separador]
    for fila in filas:
        salida.append(linea(fila))
    salida.append(separador)
    return "\n".join(salida)


class Reporte:
    """Acumula textos y tablas, los imprime en terminal y los guarda en archivos."""

    def __init__(self, titulo):
        self.titulo = titulo
        self.bloques = []

    def texto(self, s=""):
        print(s)
        self.bloques.append(("texto", s))

    def tabla(self, titulo, encabezados, filas):
        print(titulo)
        print(formatear_tabla(encabezados, filas))
        print()
        self.bloques.append(("tabla", titulo, encabezados, filas))

    def guardar(self, carpeta, nombre_base):
        os.makedirs(carpeta, exist_ok=True)
        rutas = []
        rutas.append(self._guardar_txt(os.path.join(carpeta, nombre_base + ".txt")))
        rutas.append(self._guardar_csv(os.path.join(carpeta, nombre_base + ".csv")))
        rutas.append(self._guardar_html(os.path.join(carpeta, nombre_base + ".html")))
        return rutas

    def _guardar_txt(self, ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(self.titulo + "\n" + "=" * len(self.titulo) + "\n\n")
            for bloque in self.bloques:
                if bloque[0] == "texto":
                    f.write(bloque[1] + "\n")
                else:
                    _, titulo, enc, filas = bloque
                    f.write(titulo + "\n")
                    f.write(formatear_tabla(enc, filas) + "\n\n")
        return ruta

    def _guardar_csv(self, ruta):
        # Separador ';' y BOM para que Excel en español lo abra directo en columnas.
        with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow([self.titulo])
            w.writerow([])
            for bloque in self.bloques:
                if bloque[0] == "texto":
                    if bloque[1].strip():
                        w.writerow([bloque[1].strip()])
                else:
                    _, titulo, enc, filas = bloque
                    w.writerow([titulo])
                    w.writerow(enc)
                    for fila in filas:
                        w.writerow(fila)
                    w.writerow([])
        return ruta

    def _guardar_html(self, ruta):
        partes = [
            "<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'>",
            f"<title>{html.escape(self.titulo)}</title>",
            "<style>",
            "body{font-family:Arial,sans-serif;margin:2em;max-width:1100px}",
            "h1{border-bottom:2px solid #444}h2{margin-top:2em;color:#234}",
            "table{border-collapse:collapse;margin:0.5em 0 1.5em}",
            "th,td{border:1px solid #888;padding:4px 10px;text-align:center}",
            "th{background:#dde6f0}td:first-child{font-weight:bold;background:#f3f3f3}",
            "p{margin:0.3em 0}.titulo-tabla{font-weight:bold;margin-top:1em}",
            "</style></head><body>",
            f"<h1>{html.escape(self.titulo)}</h1>",
        ]
        for bloque in self.bloques:
            if bloque[0] == "texto":
                s = bloque[1]
                if not s.strip():
                    continue
                if s.strip().startswith("==="):
                    partes.append(f"<h2>{html.escape(s.strip('= '))}</h2>")
                else:
                    partes.append(f"<p>{html.escape(s)}</p>")
            else:
                _, titulo, enc, filas = bloque
                partes.append(f"<p class='titulo-tabla'>{html.escape(titulo)}</p>")
                partes.append("<table><tr>" + "".join(f"<th>{html.escape(str(e))}</th>" for e in enc) + "</tr>")
                for fila in filas:
                    partes.append("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in fila) + "</tr>")
                partes.append("</table>")
        partes.append("</body></html>")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("\n".join(partes))
        return ruta
