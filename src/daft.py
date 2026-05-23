"""Lee los emails de alerta de Daft.ie y los convierte en anuncios.

Por que email y no la API:
  La API de Daft (gateway.daft.ie) ya esta tambien detras de Cloudflare y
  devuelve 403. Las alertas por email son la fuente fiable y estable.

Daft envia un email por cada anuncio nuevo desde:
   'Daft.ie Property Alert' <noreply@daft.ie>
Asunto:
   'Localidad, Tipo To Let, €X,XXX per month'

Como las primeras alertas suelen acabar en Spam hasta que Gmail aprende a
clasificarlas, se leen INBOX y Spam.
"""
import email
import imaplib
import re
import ssl
import time
from email.header import decode_header, make_header
from urllib.parse import urlparse

import certifi
from geopy.geocoders import Nominatim

from . import config

# Cache de geocodificacion (memoria) para no repetir llamadas a Nominatim.
_GEO = None
_CACHE_GEO = {}


def _geo_cliente():
    global _GEO
    if _GEO is None:
        # SSL explicito con certifi: el Python de macOS no encuentra el
        # certificado raiz por defecto y daria error de SSL.
        ctx = ssl.create_default_context(cafile=certifi.where())
        _GEO = Nominatim(user_agent="ireland-house-finder", ssl_context=ctx)
    return _GEO


def _geocodificar(localidad):
    """Devuelve (lat, lon) de la localidad en Cork, o None si no se encuentra."""
    if not localidad:
        return None
    key = localidad.lower()
    if key in _CACHE_GEO:
        return _CACHE_GEO[key]
    try:
        time.sleep(1.0)  # Nominatim limita a 1 peticion por segundo
        loc = _geo_cliente().geocode(f"{localidad}, Cork, Ireland", timeout=20)
        result = (loc.latitude, loc.longitude) if loc else None
    except Exception:
        result = None
    _CACHE_GEO[key] = result
    return result


def _texto_de_html(html):
    txt = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", txt).strip()


def _titulo_legible(url, fallback):
    """A partir del slug de la URL construye un titulo legible.

    Ejemplo: /for-rent/house-dungourney-dungourney-co-cork/6575750
           -> 'Dungourney Dungourney Co Cork'
    """
    path = urlparse(url).path
    parts = [p for p in path.split("/") if p]
    slug = parts[-2] if len(parts) >= 2 else ""
    slug = re.sub(r"^(house|apartment|bungalow|studio|duplex|townhouse|property)-", "", slug)
    palabras = " ".join(w.capitalize() for w in slug.split("-"))
    return palabras or fallback


def _parsear_asunto(subject):
    """Saca (localidad, tipo, precio_mes, precio_texto) del asunto del email."""
    m = re.match(
        r"(.+?),\s*(House|Apartment|Bungalow|Studio|Duplex|Townhouse|Property)\s+To Let,\s*€([\d,]+)\s*per\s*(month|week)",
        subject,
    )
    if not m:
        return None
    localidad = m.group(1).strip()
    tipo = m.group(2)
    n = int(m.group(3).replace(",", ""))
    if m.group(4) == "week":
        precio_mes = round(n * 52 / 12)
        precio_texto = f"€{n} per week"
    else:
        precio_mes = n
        precio_texto = f"€{n:,} per month"
    return localidad, tipo, precio_mes, precio_texto


def _parsear_email(msg):
    """Convierte un email de alerta en un dict de anuncio. None si no encaja."""
    subject = str(make_header(decode_header(msg.get("Subject", ""))))

    html_body = ""
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html_body = part.get_payload(decode=True).decode(errors="replace")
            break
    text = _texto_de_html(html_body)

    urls = re.findall(r"https://www\.daft\.ie/for-rent/[^\"\s<>?]+", html_body)
    if not urls:
        return None
    url = urls[0]
    m_id = re.search(r"/(\d+)$", url.rstrip("/"))
    listing_id = int(m_id.group(1)) if m_id else None
    if not listing_id:
        return None

    info = _parsear_asunto(subject)
    if info:
        localidad, tipo, precio_mes, precio_texto = info
    else:
        # Formato de dirección completa: extraer tipo de la URL y precio del cuerpo
        path = urlparse(url).path
        tipo = "House"
        for t in ("apartment", "bungalow", "studio", "duplex", "townhouse"):
            if f"/{t}-" in path:
                tipo = t.capitalize()
                break
        m_precio = re.search(r"€([\d,]+)\s*per\s*(month|week)", text, re.IGNORECASE)
        if not m_precio:
            return None
        n = int(m_precio.group(1).replace(",", ""))
        if m_precio.group(2).lower() == "week":
            precio_mes = round(n * 52 / 12)
            precio_texto = f"€{n} per week"
        else:
            precio_mes = n
            precio_texto = f"€{n:,} per month"
        # Localidad: última parte significativa del asunto (excluyendo "Co. Cork")
        partes = [p.strip() for p in subject.split(",")]
        partes = [p for p in partes if p and not re.match(r"^co\.?\s*cork$", p, re.IGNORECASE)]
        localidad = partes[-1] if partes else ""

    m_b = re.search(r"(\d+)\s*Bed", text)
    beds = int(m_b.group(1)) if m_b else None
    m_ba = re.search(r"(\d+)\s*Bath", text)
    baths = int(m_ba.group(1)) if m_ba else None
    m_ber = re.search(r"\bBER\s+([A-G][12]?)\b", text)
    ber = m_ber.group(1) if m_ber else None

    coords = _geocodificar(localidad)
    lat, lon = coords if coords else (None, None)

    return {
        "id": listing_id,
        "titulo": _titulo_legible(url, localidad),
        "url": url,
        "precio_texto": precio_texto,
        "precio_mes": precio_mes,
        "habitaciones": beds,
        "banos": baths,
        "tipo": tipo,
        "ber": ber,
        "lon": lon,
        "lat": lat,
        "publicado_ms": None,
        "vendedor": "",
        "tipo_vendedor": "",
        "mascotas": None,  # los emails no detallan servicios fiablemente
    }


def buscar(min_beds=3, max_anuncios=300):
    """Lee los emails de alerta de Daft (INBOX + Spam) y devuelve los anuncios.

    El parametro min_beds se mantiene por compatibilidad pero ya no filtra:
    la propia alerta guardada en Daft impone ese minimo en origen.
    """
    cfg = config.cargar()
    g = cfg["gmail"]
    m = imaplib.IMAP4_SSL("imap.gmail.com")
    m.login(g["usuario"], g["app_password"])
    try:
        resultados = []
        vistos = set()
        for carpeta in ["INBOX", '"[Gmail]/Spam"', '"aa Ireland Houses"']:
            try:
                typ, _ = m.select(carpeta)
                if typ != "OK":
                    continue
            except Exception:
                continue
            typ, nums = m.search(None, '(FROM "Daft.ie Property Alert")')
            if not nums or not nums[0]:
                continue
            ids = nums[0].split()
            # Procesar primero los mas recientes (UIDs altos).
            for uid in reversed(ids[-max_anuncios:]):
                typ, d = m.fetch(uid, "(RFC822)")
                if typ != "OK" or not d or not d[0]:
                    continue
                anun = _parsear_email(email.message_from_bytes(d[0][1]))
                if not anun or anun["id"] in vistos:
                    continue
                resultados.append(anun)
                vistos.add(anun["id"])
        return resultados
    finally:
        try:
            m.logout()
        except Exception:
            pass
