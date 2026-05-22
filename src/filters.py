"""Aplica los filtros de busqueda a un anuncio ya normalizado."""
from .geo import distancia_km


def evaluar(anuncio, filtros, referencias):
    """Evalua si un anuncio cumple los requisitos.

    Devuelve un diccionario con:
      - cumple: True/False
      - motivos: razones por las que se descarta (si las hay)
      - avisos: cosas que hay que comprobar a mano (no se pueden filtrar)
      - dist_centro / dist_cuh: distancias en km (o None)
    """
    motivos = []
    avisos = []

    hab = anuncio["habitaciones"]
    if hab is not None and hab < filtros["habitaciones_min"]:
        motivos.append(f"solo {hab} habitacion(es)")

    ban = anuncio["banos"]
    if ban is None:
        avisos.append("banos no indicados")
    elif ban < filtros["banos_min"]:
        motivos.append(f"solo {ban} bano(s)")

    precio = anuncio["precio_mes"]
    if precio is None:
        avisos.append("precio no indicado")
    elif precio > filtros["precio_max_eur"]:
        motivos.append(f"precio {precio} EUR/mes")

    dist_centro = dist_cuh = None
    if anuncio["lat"] is not None:
        dist_centro = distancia_km(
            anuncio["lat"], anuncio["lon"],
            referencias["centro_lat"], referencias["centro_lon"],
        )
        dist_cuh = distancia_km(
            anuncio["lat"], anuncio["lon"],
            referencias["cuh_lat"], referencias["cuh_lon"],
        )
        if dist_centro > filtros["distancia_max_km"]:
            motivos.append(f"a {dist_centro} km del centro")
    else:
        avisos.append("sin coordenadas GPS")

    # Estos dos datos no estan en la API de Daft: hay que mirarlos en el anuncio.
    if filtros.get("requiere_amueblada"):
        avisos.append("comprobar si esta amueblada")
    avisos.append("comprobar disponibilidad (julio/agosto 2026)")

    return {
        "cumple": len(motivos) == 0,
        "motivos": motivos,
        "avisos": avisos,
        "dist_centro": dist_centro,
        "dist_cuh": dist_cuh,
    }
