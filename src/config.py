"""Carga la configuracion desde config.yaml."""
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent


def cargar():
    """Lee config.yaml y devuelve un diccionario con toda la configuracion."""
    ruta = RAIZ / "config.yaml"
    if not ruta.exists():
        raise SystemExit(
            "No existe config.yaml. Copia config.example.yaml como config.yaml "
            "y rellena tus datos."
        )
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f)
