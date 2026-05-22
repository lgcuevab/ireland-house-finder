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
- [x] **Fase 5** - Despliegue 24/7 en GitHub Actions (cada 5 min).

## Estado actual

**Fases 1, 2, 3 y 5 COMPLETAS.** El bot trabaja solo 24/7 en GitHub Actions
(repo: github.com/lgcuevab/ireland-house-finder). Cada 5 minutos:

  1. Lee las alertas de Daft en Gmail (INBOX + Spam).
  2. Filtra por requisitos y descarta repetidos.
  3. Por cada casa nueva que cumple, envia por Telegram a Lucho y a Esther:
     a) El aviso con los datos del anuncio.
     b) La presentacion de la solicitud (copiar y pegar).
     c) El parrafo sobre el perrito (copiar y pegar).
  4. Anyade la fila al Google Sheet.

Solo queda la Fase 4 (anyadir MyHome.ie, Rent.ie y FindAHome.ie cuando
Lucho cree las alertas guardadas en esos portales).

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
