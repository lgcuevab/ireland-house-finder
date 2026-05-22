"""Calculo de distancias en linea recta (formula de Haversine)."""
from math import asin, cos, radians, sin, sqrt

RADIO_TIERRA_KM = 6371.0


def distancia_km(lat1, lon1, lat2, lon2):
    """Distancia en linea recta (km) entre dos puntos GPS."""
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    return round(2 * RADIO_TIERRA_KM * asin(sqrt(a)), 1)
