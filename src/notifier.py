"""Envia los avisos por Telegram.

Mientras Telegram no este configurado en config.yaml, los avisos se muestran
por la consola para poder probar el resto del programa.
"""
import requests

PENDIENTE = (None, "", "PENDIENTE")


def telegram_configurado(cfg):
    t = cfg.get("telegram", {})
    return t.get("bot_token") not in PENDIENTE and bool(t.get("chat_ids"))


def enviar(cfg, texto):
    """Envia un mensaje a todos los chats configurados.

    Si Telegram no esta listo, lo imprime por consola.
    """
    if not telegram_configurado(cfg):
        print("\n[Telegram aun no configurado - se muestra por consola]")
        print(texto)
        print("-" * 60)
        return
    t = cfg["telegram"]
    url = f"https://api.telegram.org/bot{t['bot_token']}/sendMessage"
    for chat_id in t["chat_ids"]:
        r = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": texto,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=20,
        )
        r.raise_for_status()
