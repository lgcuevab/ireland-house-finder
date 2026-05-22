"""Base de datos local (SQLite) para no avisar dos veces del mismo anuncio."""
import sqlite3
from datetime import datetime
from pathlib import Path

RUTA = Path(__file__).resolve().parent.parent / "data" / "vistos.db"


def _conexion():
    RUTA.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(RUTA)
    con.execute(
        "CREATE TABLE IF NOT EXISTS vistos (id INTEGER PRIMARY KEY, visto_en TEXT)"
    )
    return con


def ids_vistos():
    """Devuelve el conjunto de ids de anuncios ya procesados."""
    con = _conexion()
    ids = {fila[0] for fila in con.execute("SELECT id FROM vistos")}
    con.close()
    return ids


def marcar(ids):
    """Guarda una lista de ids como ya vistos."""
    con = _conexion()
    ahora = datetime.now().isoformat(timespec="seconds")
    con.executemany(
        "INSERT OR IGNORE INTO vistos (id, visto_en) VALUES (?, ?)",
        [(i, ahora) for i in ids],
    )
    con.commit()
    con.close()


def esta_vacia():
    """True si todavia no se ha guardado ningun anuncio (primera ejecucion)."""
    con = _conexion()
    n = con.execute("SELECT COUNT(*) FROM vistos").fetchone()[0]
    con.close()
    return n == 0
