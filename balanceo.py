"""Balanceo del problema: agrega un origen o destino ficticio si hace falta."""

from utilidades import fmt


def balancear(costos, oferta, demanda, nombres_f, nombres_c, reporte):
    """Devuelve copias balanceadas de costos, oferta, demanda y nombres."""
    costos = [list(f) for f in costos]
    oferta = list(oferta)
    demanda = list(demanda)
    nombres_f = list(nombres_f)
    nombres_c = list(nombres_c)

    total_oferta = sum(oferta)
    total_demanda = sum(demanda)
    reporte.texto(f"Oferta total = {fmt(total_oferta)}, demanda total = {fmt(total_demanda)}.")

    if total_oferta > total_demanda:
        faltante = total_oferta - total_demanda
        for fila in costos:
            fila.append(0)
        demanda.append(faltante)
        nombres_c.append("Ficticio")
        reporte.texto(f"La oferta excede a la demanda. Se agrega un destino ficticio "
                      f"con demanda {fmt(faltante)} y costo 0.")
    elif total_demanda > total_oferta:
        faltante = total_demanda - total_oferta
        costos.append([0] * len(demanda))
        oferta.append(faltante)
        nombres_f.append("Ficticio")
        reporte.texto(f"La demanda excede a la oferta. Se agrega un origen ficticio "
                      f"con oferta {fmt(faltante)} y costo 0.")
    else:
        reporte.texto("El problema está balanceado.")

    return costos, oferta, demanda, nombres_f, nombres_c
