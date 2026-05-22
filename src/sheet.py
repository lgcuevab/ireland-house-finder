"""Escribe en el Google Sheet 'Ireland Properties Contacted'.

Se conecta con la cuenta de servicio (credentials/service-account.json) y
anyade cada casa nueva al final de la primera pestana, evitando duplicar
URLs que ya esten en la hoja.

Columnas de la pestana 'Cork y Eje Cork Bantry - House' (las 5 que cuentan):
    A: URL
    B: Contactado email / formulario   (lo rellena Lucho a mano)
    C: Fecha 1o contacto               (lo rellena Lucho a mano)
    D: price
    E: Notes / Distance to CUH

La columna F (Seguimiento) y las siguientes no se tocan.
"""
import gspread

from .config import RAIZ

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Cache de conexion para no abrir el Sheet en cada llamada del mismo ciclo.
_hoja_cache = None


def _ruta_credenciales(cfg):
    ruta = cfg["google_sheet"]["credenciales_json"]
    if not ruta.startswith("/"):
        ruta = str(RAIZ / ruta)
    return ruta


def _abrir(cfg):
    global _hoja_cache
    if _hoja_cache is not None:
        return _hoja_cache
    gc = gspread.service_account(filename=_ruta_credenciales(cfg), scopes=SCOPES)
    sh = gc.open_by_key(cfg["google_sheet"]["sheet_id"])
    nombre = cfg["google_sheet"].get("pestana")
    try:
        ws = sh.worksheet(nombre) if nombre else sh.sheet1
    except gspread.WorksheetNotFound:
        ws = sh.sheet1
    _hoja_cache = ws
    return ws


def _formato_precio(precio_mes):
    """Da formato '€2,500.00', como las filas que Lucho ha escrito a mano."""
    if precio_mes is None:
        return ""
    return f"€{precio_mes:,.2f}"


def _formato_notas(anuncio, ev):
    partes = []
    if ev.get("dist_cuh") is not None:
        partes.append(f"{ev['dist_cuh']} km CUH (linea recta)")
    if anuncio.get("mascotas") is True:
        partes.append("admite mascotas")
    if anuncio.get("ber"):
        partes.append(f"BER {anuncio['ber']}")
    return ", ".join(partes)


def url_existe(ws_o_cfg, url):
    """True si esa URL ya esta en la columna A del Sheet.

    Acepta tanto una worksheet ya abierta como la configuracion (la abre).
    Comprueba la URL tal cual y tambien sin parametros de query.
    """
    ws = ws_o_cfg if hasattr(ws_o_cfg, "col_values") else _abrir(ws_o_cfg)
    base = url.split("?")[0]
    for u in ws.col_values(1):
        if not u:
            continue
        if u == url or u.split("?")[0] == base:
            return True
    return False


def anadir_fila(cfg, anuncio, ev):
    """Anyade una fila para la casa indicada, si su URL no estaba ya.

    Devuelve:
        'added'      -> se escribio una nueva fila
        'duplicate'  -> la URL ya estaba en el Sheet (no se hace nada)
    """
    ws = _abrir(cfg)
    if url_existe(ws, anuncio["url"]):
        return "duplicate"
    siguiente = len(ws.col_values(1)) + 1
    fila = [
        anuncio["url"],
        "",  # Contactado email / formulario
        "",  # Fecha 1o contacto
        _formato_precio(anuncio["precio_mes"]),
        _formato_notas(anuncio, ev),
    ]
    ws.update(
        f"A{siguiente}:E{siguiente}",
        [fila],
        value_input_option="USER_ENTERED",
    )
    return siguiente  # devuelve el numero de fila escrita
