"""Construye y envia por Telegram los borradores que Lucho copia y pega
en el formulario de contacto del anuncio.

Los textos se mantienen en archivos sueltos (mensajes/presentacion.txt y
mensajes/mascota.txt) para que Lucho pueda editarlos cuando quiera sin
tocar el codigo.
"""
import html

from . import notifier
from .config import RAIZ

_CACHE = {}


def _leer(nombre):
    """Lee un fichero de la carpeta mensajes/ con cache en memoria."""
    if nombre in _CACHE:
        return _CACHE[nombre]
    ruta = RAIZ / "mensajes" / nombre
    if not ruta.exists():
        raise FileNotFoundError(f"No se encuentra {ruta}")
    _CACHE[nombre] = ruta.read_text(encoding="utf-8").strip()
    return _CACHE[nombre]


def enviar_borradores(cfg, anuncio):
    """Envia por Telegram los dos borradores asociados a un anuncio.

    Devuelve True si se enviaron, False si Telegram no esta configurado.
    """
    titulo = html.escape(anuncio.get("titulo", ""))
    presentacion = html.escape(_leer("presentacion.txt"))
    mascota = html.escape(_leer("mascota.txt"))

    # Mensaje 1: presentacion de la solicitud
    notifier.enviar(
        cfg,
        f"\U0001F4E9 <b>Presentacion para {titulo}</b>\n"
        f"(copia este texto y pegalo en el formulario de Daft)\n\n"
        f"{presentacion}",
    )
    # Mensaje 2: parrafo sobre el perrito (si encaja en este anuncio)
    notifier.enviar(
        cfg,
        f"\U0001F436 <b>Sobre el perrito</b>\n"
        f"(parrafo extra para anyadir si el anuncio admite mascotas o no lo indica)\n\n"
        f"{mascota}",
    )
    return notifier.telegram_configurado(cfg)
