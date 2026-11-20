"""Programa principal: resuelve un problema de transporte.

1. Obtiene una solución básica factible (Esquina Noroeste, Costo Mínimo o Vogel).
2. La optimiza con el método DIMO.
3. Muestra todo en la terminal y lo guarda en resultados/ como .txt, .csv y .html.

Uso:
    python3 main.py                  (captura interactiva o lectura de archivo)
    python3 main.py ejemplos/ejemplo1.txt
"""

import os
import sys

from balanceo import balancear
from dimo import dimo
from metodos_iniciales import METODOS
from utilidades import Reporte, tabla_transporte

CARPETA_RESULTADOS = "resultados"


def a_numero(texto):
    texto = texto.strip().replace(",", ".")
    valor = float(texto)
    return int(valor) if valor.is_integer() else valor


def leer_lista(mensaje, cantidad):
    """Lee 'cantidad' números separados por espacios, reintentando si hay error."""
    while True:
        try:
            valores = [a_numero(t) for t in input(mensaje).split()]
            if len(valores) != cantidad:
                print(f"  Se esperaban {cantidad} valores y se recibieron {len(valores)}.")
                continue
            if any(x < 0 for x in valores):
                print("  Los valores no pueden ser negativos.")
                continue
            return valores
        except ValueError:
            print("  Entrada no válida. Escribe solo números separados por espacios.")


def leer_entero(mensaje, minimo=1):
    while True:
        try:
            x = int(input(mensaje))
            if x < minimo:
                print(f"  Debe ser al menos {minimo}.")
                continue
            return x
        except ValueError:
            print("  Escribe un número entero.")


def capturar_manual():
    print("\n--- Captura de datos ---")
    m = leer_entero("Número de orígenes (filas): ")
    n = leer_entero("Número de destinos (columnas): ")
    print(f"\nEscribe la matriz de costos, una fila por línea ({n} valores por fila):")
    costos = [leer_lista(f"  Costos del origen O{i + 1}: ", n) for i in range(m)]
    oferta = leer_lista(f"\nOferta de los {m} orígenes: ", m)
    demanda = leer_lista(f"Demanda de los {n} destinos: ", n)
    return costos, oferta, demanda


def leer_archivo(ruta):
    """Formato del archivo:

        oferta: 35 50 40
        demanda: 45 20 30 30
        costos:
        8 6 10 9
        9 12 13 7
        14 9 16 5

    Las líneas que empiezan con # se ignoran.
    """
    oferta = demanda = None
    costos = []
    leyendo_costos = False
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            minus = linea.lower()
            if minus.startswith("oferta:"):
                oferta = [a_numero(t) for t in linea.split(":", 1)[1].split()]
                leyendo_costos = False
            elif minus.startswith("demanda:"):
                demanda = [a_numero(t) for t in linea.split(":", 1)[1].split()]
                leyendo_costos = False
            elif minus.startswith("costos:"):
                leyendo_costos = True
            elif leyendo_costos:
                costos.append([a_numero(t) for t in linea.split()])
    if oferta is None or demanda is None or not costos:
        raise ValueError("El archivo debe incluir 'oferta:', 'demanda:' y 'costos:'.")
    if len(costos) != len(oferta) or any(len(fila) != len(demanda) for fila in costos):
        raise ValueError("Las dimensiones de la matriz de costos no coinciden con oferta y demanda.")
    return costos, oferta, demanda


def elegir_metodos():
    print("\n--- Método para la solución inicial ---")
    for clave, (nombre, _, _) in METODOS.items():
        print(f"  {clave}) {nombre}")
    print("  4) Los tres (comparar)")
    while True:
        opcion = input("Elige una opción: ").strip()
        if opcion in METODOS:
            return [METODOS[opcion]]
        if opcion == "4":
            return list(METODOS.values())
        print("  Opción no válida.")


def resolver(costos, oferta, demanda, nombre, funcion, clave_archivo):
    nombres_f = [f"O{i + 1}" for i in range(len(costos))]
    nombres_c = [f"D{j + 1}" for j in range(len(costos[0]))]

    reporte = Reporte(f"Problema de transporte - {nombre} + DIMO")
    reporte.texto("\n=== Datos del problema ===")
    enc, fil = tabla_transporte(costos, [[0] * len(costos[0]) for _ in costos], set(),
                                oferta, demanda, nombres_f, nombres_c)
    reporte.tabla("Costos [c_ij], oferta y demanda:", enc, fil)

    costos_b, oferta_b, demanda_b, nombres_f, nombres_c = balancear(
        costos, oferta, demanda, nombres_f, nombres_c, reporte)

    asignacion, basicas = funcion(costos_b, oferta_b, demanda_b, nombres_f, nombres_c, reporte)
    dimo(costos_b, asignacion, basicas, oferta_b, demanda_b, nombres_f, nombres_c, reporte)

    rutas = reporte.guardar(CARPETA_RESULTADOS, f"reporte_{clave_archivo}")
    print("\nReporte guardado en:")
    for r in rutas:
        print("  " + os.path.abspath(r))


def main():
    print("=" * 60)
    print("   RESOLUCIÓN DEL PROBLEMA DE TRANSPORTE")
    print("   Solución inicial + optimización con DIMO")
    print("=" * 60)

    if len(sys.argv) > 1:
        costos, oferta, demanda = leer_archivo(sys.argv[1])
        print(f"Datos leídos de {sys.argv[1]}")
    else:
        print("\n¿Cómo quieres ingresar los datos?")
        print("  1) Capturarlos a mano")
        print("  2) Leerlos de un archivo")
        while True:
            opcion = input("Elige una opción: ").strip()
            if opcion == "1":
                costos, oferta, demanda = capturar_manual()
                break
            if opcion == "2":
                ruta = input("Ruta del archivo: ").strip()
                try:
                    costos, oferta, demanda = leer_archivo(ruta)
                    break
                except (OSError, ValueError) as e:
                    print(f"  No se pudo leer el archivo: {e}")
            else:
                print("  Opción no válida.")

    for nombre, funcion, clave in elegir_metodos():
        print("\n" + "#" * 60)
        print(f"#  {nombre}")
        print("#" * 60)
        resolver(costos, oferta, demanda, nombre, funcion, clave)


if __name__ == "__main__":
    main()
