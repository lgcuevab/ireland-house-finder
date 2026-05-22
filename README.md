# Ireland House Finder

Automatización para encontrar casa de alquiler en **Cork (Irlanda)** lo antes posible.

## Qué hace

```
Daft.ie + (futuro: MyHome / Rent.ie / FindAHome)  ->  alertas por email a Gmail
   (Daft envia un email por cada anuncio nuevo; la API y la web estan
    bloqueadas por Cloudflare, asi que email es la fuente fiable)
        |
        v
   Automatizacion (servidor 24/7)
   - lee y parsea los emails (INBOX + Spam)
   - geocodifica la localidad y calcula distancia al centro y a CUH
   - extrae los datos del anuncio
   - filtra por los requisitos
   - descarta anuncios repetidos
        |
        +--> 1) Aviso por Telegram (Lucho + Esther)
        +--> 2) Fila nueva en el Google Sheet
        +--> 3) Borrador de mensaje (presentacion + mascota)
```

## Requisitos de la vivienda

| Filtro        | Valor                                    |
|---------------|------------------------------------------|
| Ubicacion     | Cork City o <= 50 km del centro          |
| Habitaciones  | >= 3                                     |
| Banos         | >= 2                                     |
| Amueblada     | Si                                       |
| Precio        | <= 3.000 EUR/mes                         |
| Disponible    | Julio o agosto 2026                      |
| Mascota       | No se excluye; se anota lo que diga      |

## Estructura del proyecto

```
ireland-house-finder/
  README.md                <- este fichero
  requirements.txt         <- librerias de Python
  config.example.yaml      <- plantilla de configuracion
  config.yaml              <- tu configuracion real (NO se comparte)
  .gitignore
  Cork Accommodation.pdf   <- documento de referencia
  mensajes/
    presentacion.txt       <- Copy de presentacion de la solicitud
    mascota.txt            <- Copy sobre el perrito
  credentials/             <- clave de Google (NO se comparte)
  data/                    <- base de datos local de anuncios vistos
  src/                     <- codigo de la automatizacion (Fase 1+)
```

## Plan por fases

- [x] **Fase 1** - MVP: leer alertas de Daft, filtrar, distancias y avisar por Telegram.
- [x] **Tarea D** - Cuenta de servicio de Google.
- [x] **Fase 2** - Escribir cada casa nueva en el Google Sheet.
- [x] **Fase 3** - Generar borradores de mensaje (presentacion + mascota).
- [ ] **Fase 4** - Anadir mas portales (MyHome, Rent.ie, FindAHome) por email.
- [ ] **Fase 5** - Desplegar en la nube 24/7 (ahora solo se ejecuta a mano).

## Estado actual

**Fases 1, 2 y 3 COMPLETAS.** Para cada casa nueva que cumple los filtros
el bot envia por Telegram (a Lucho y a Esther):
  1. El aviso con los datos del anuncio.
  2. La presentacion de la solicitud (lista para copiar y pegar).
  3. El parrafo sobre el perrito (lista para copiar y pegar).
Y anyade la fila correspondiente al Google Sheet.

Siguiente: Fase 4 (mas portales) y Fase 5 (despliegue 24/7; ahora mismo
el bot solo trabaja cuando se lanza a mano).

Accion pendiente para Lucho (cuando pueda):
  - Marcar las alertas de Daft como "No es spam" en Gmail y crear un
    filtro para que no vuelvan a ir a la carpeta de Spam. El bot ya lee
    Spam por si acaso, pero es mas limpio tenerlas en la bandeja.

## Como ejecutarlo a mano

Desde la carpeta del proyecto:

    .venv/bin/python -m src.main

La primera vez guarda la "linea base" sin avisar. Las siguientes veces avisa
solo de las casas NUEVAS que cumplen los requisitos. Hasta la Fase 5 no se
ejecuta solo: hay que lanzarlo.
