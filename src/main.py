"""Punto de entrada: busca casas nuevas en Daft.ie y avisa de las que cumplen.

Ejecucion (desde la carpeta del proyecto):
    .venv/bin/python -m src.main
"""
import html
from datetime import datetime

from . import config, daft, notifier, sheet, storage
from .filters import evaluar


def formatear(anuncio, ev):
    """Construye el texto del aviso para Telegram."""
    lineas = [
        f"\U0001F3E0 <b>{html.escape(anuncio['titulo'])}</b>",
        f"\U0001F4B6 {anuncio['precio_texto']}  |  {anuncio['habitaciones']} hab  |  "
        f"{anuncio['banos'] or '?'} bano(s)",
        f"\U0001F3F7 {anuncio['tipo']}  |  BER {anuncio['ber'] or '?'}",
    ]
    if ev["dist_centro"] is not None:
        lineas.append(
            f"\U0001F4CD {ev['dist_centro']} km del centro  ·  "
            f"{ev['dist_cuh']} km de CUH (linea recta)"
        )
    if anuncio["mascotas"] is True:
        lineas.append("\U0001F436 El anuncio indica que admite mascotas")
    if ev["avisos"]:
        lineas.append("⚠️ Revisar a mano: " + "; ".join(ev["avisos"]))
    lineas.append(anuncio["url"])
    return "\n".join(lineas)


def ciclo():
    """Ejecuta una ronda completa: consultar, filtrar y avisar."""
    cfg = config.cargar()
    filtros = cfg["filtros"]
    referencias = cfg["referencias"]

    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Consultando la API de Daft.ie ...")
    anuncios = daft.buscar(min_beds=filtros["habitaciones_min"])
    print(f"  {len(anuncios)} anuncios de Cork recibidos.")

    # Quedarnos con los que cumplen TODOS los requisitos.
    candidatos = []
    for a in anuncios:
        ev = evaluar(a, filtros, referencias)
        if ev["cumple"]:
            candidatos.append((a, ev))
    print(f"  {len(candidatos)} cumplen los filtros (precio, habitaciones, banos, distancia).")

    # Primera ejecucion: guardar la linea base y NO avisar (evita una avalancha).
    if storage.esta_vacia():
        storage.marcar([a["id"] for a in anuncios])
        print(f"\n  Primera ejecucion: guardada la linea base de {len(anuncios)} anuncios.")
        print(f"  Casas que YA cumplen tus requisitos ahora mismo ({len(candidatos)}):\n")
        for a, ev in candidatos:
            dist = f"{ev['dist_centro']} km centro" if ev["dist_centro"] is not None else "sin GPS"
            print(f"   - {a['titulo']}")
            print(f"     {a['precio_texto']} | {a['habitaciones']} hab | "
                  f"{a['banos'] or '?'} bano(s) | {dist}")
            print(f"     {a['url']}\n")
        print("  A partir de la proxima ejecucion solo se avisara de las NUEVAS.")
        return

    # Ejecuciones siguientes: avisar solo de los candidatos que no se habian visto.
    vistos = storage.ids_vistos()
    nuevos = [(a, ev) for a, ev in candidatos if a["id"] not in vistos]
    print(f"  {len(nuevos)} casa(s) NUEVA(S) que cumplen los requisitos.")

    for a, ev in nuevos:
        # 1) Aviso por Telegram con los datos del anuncio.
        notifier.enviar(cfg, formatear(a, ev))
        # 2) Anyadir fila al Google Sheet (sin romper el ciclo si falla).
        try:
            resultado = sheet.anadir_fila(cfg, a, ev)
            if resultado == "duplicate":
                print(f"  - ya estaba en el Sheet: {a['url']}")
            else:
                print(f"  + escrito en el Sheet (fila {resultado}): {a['titulo']}")
        except Exception as e:
            print(f"  ! ERROR al escribir en el Sheet: {repr(e)[:200]}")

    # Marcar como vistos todos los anuncios recibidos (cumplan o no).
    storage.marcar([a["id"] for a in anuncios])


if __name__ == "__main__":
    ciclo()
