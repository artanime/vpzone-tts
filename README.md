# VPZone TTS

Lector de chat por voz para VPZone. Se conecta al WebSocket del chat, filtra y
prioriza los mensajes y los convierte en voz, con una interfaz de escritorio.

## Características

- Interfaz gráfica en **CustomTkinter** (conexión, voz, volumen, filtros y log en vivo).
- Motores de voz:
  - **Piper** (neuronal, offline, por defecto; no depende de Microsoft).
  - **pyttsx3** (SAPI5, offline).
  - **edge-tts** (voces de Microsoft, online; puede ser bloqueado con error 403).
- Reproducción de audio con **pygame-ce** (fallback a `ffplay`).
- **Filtros** de chat: longitud, enlaces, emojis, anti-repetición y anti-spam.
- **Selector de idioma** de la interfaz: español, inglés, francés y ruso (cambio en vivo).
- **Cola con prioridad** (moderadores/streamer pasan primero).
- **Sistema de eventos** y **plugins** (carpeta `plugins/`).
- Cliente REST + WebSocket de la API de VPZone.
- Cliente REST + EventSub de la API de **Woupi** (plataforma seleccionable).
- **Acceso a Woupi sin secretos**: asistente de autorización por *código de
  dispositivo*; el usuario conecta su propia cuenta y los tokens se guardan en
  `config/secrets.json` (nunca en `config.json`).
- **Número de versión** visible en la interfaz y en el título de la ventana.
- Reconexión automática del WebSocket con backoff exponencial.

## Requisitos

- Windows con **Python 3.10+** (desarrollado en 3.14).
- Sistemas de voz SAPI5 instalados (Windows ya trae algunas).

## Instalación

```powershell
cd VPZoneTTS
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt

# Crea tu configuración local a partir de la plantilla (no se sube al repo)
Copy-Item config\config.example.json config\config.json

# Crea tus secretos locales a partir de la plantilla (no se sube al repo)
Copy-Item .env.example .env
```

> `config/config.json`, `.env` y `config/secrets.json` están en `.gitignore` y
> **nunca deben subirse**. Al publicar solo se comparten `config/config.example.json`
> y `.env.example`.
>
> Los secretos (`api_key`, `access_token`, `refresh_token`) ya
> **no** se guardan en `config.json`. Se leen de variables de entorno / `.env`, y
> los tokens que genera la app se guardan en `config/secrets.json`.

## Uso

```powershell
# Interfaz gráfica (por defecto)
.\.venv\Scripts\python app.py

# Modo consola sin interfaz
.\.venv\Scripts\python app.py --headless
```

En la interfaz:

1. Escribe el **canal** y pulsa *Aplicar*.
2. Elige **proveedor** y **voz** (pulsa *Actualizar* para recargar la lista).
3. Ajusta volumen y velocidad.
4. Pulsa **Conectar chat** para empezar a leer los mensajes.
5. Usa **Probar voz** para escuchar sin necesidad de conectar al chat.
6. Si eliges **Woupi** como plataforma, pulsa **Cuenta Woupi** la primera vez
   para autorizar tu cuenta con un código (ver más abajo).

## Configuración (`config/config.json`)

El archivo real es **local** (ignorado por git). Se crea a partir de
`config/config.example.json`; si no existe, la app lo genera con los valores por
defecto de `config/defaults.py`.

Este archivo **solo contiene datos no secretos**: los secretos viven en `.env` /
`config/secrets.json` (ver [Credenciales y secretos](#credenciales-y-secretos)).

| Clave | Descripción |
|---|---|
| `language` | Idioma de la interfaz: `es`, `en`, `fr` o `ru`. |
| `platform` | Plataforma de chat: `vpzone` o `woupi`. |
| `channel` | Canal del que se leen los mensajes (slug en VPZone, login en Woupi). |
| `api_base_url` | API REST de VPZone (opcional). |
| `websocket_url` | Endpoint del chat de VPZone (por defecto `wss://chat.vpzone.tv/ws`). |
| `woupi.*` | Endpoints y datos no secretos de Woupi (ver abajo). |
| `tts.provider` | `piper`, `pyttsx3`, `edge`, `debug` o `fake`. |
| `tts.voice` | Voz (`default` usa la predeterminada del sistema). |
| `tts.volume` / `tts.speed` | Volumen (0-100) y velocidad (0.5-2.0). |
| `tts.read_username` | Leer el nombre del usuario antes del mensaje. |
| `tts.skip_history` | Al conectar, no leer el historial antiguo (pide solo mensajes nuevos y vacía la cola). |
| `tts.filters.*` | Activar/desactivar cada filtro. |

La configuración se guarda automáticamente al cambiarla desde la interfaz.

### Credenciales y secretos

Los secretos **nunca** se escriben en `config/config.json`. Se resuelven así
(`core/secrets_store.py`):

| Fuente | Contenido | ¿Se sube a git? |
|---|---|---|
| `.env` (raíz) | Valores que pones tú: `VPZONE_API_KEY`; opcionalmente `WOUPI_ACCESS_TOKEN` / `WOUPI_REFRESH_TOKEN`. | No (`.gitignore`) |
| `config/secrets.json` | Tokens que genera la app (OAuth y renovaciones). | No (`.gitignore`) |
| Variables de entorno | Iguales que `.env`; tienen prioridad. | — |

Reglas de prioridad:

- `api_key`: gana el entorno sobre `secrets.json`.
- `access_token` y `refresh_token`: gana `secrets.json` (la app los rota sola);
  `.env` solo sirve como carga inicial.

El `client_id` de Woupi es **público** y se queda en `config/config.json`.

### Conectar con Woupi

Woupi no entrega el chat por un WebSocket directo: usa **EventSub**. La app
abre `wss://api.woupi.buzz/eventsub`, espera el `session_welcome` y crea una
suscripción `channel.chat.message` en los primeros 10 segundos.

Requisitos:

1. Una app creada en <https://dev.woupi.buzz> (categoría `chat_bot`).
2. Su **Client ID** (público, no es un secreto). Es lo único que necesita la
   app para autorizar al usuario.
3. Opcional: un **refresh token** para renovar el access token (4 h) solo.

#### Opción recomendada: código de dispositivo (sin secretos)

La aplicación **no lleva credenciales propias**. Cada usuario autoriza su
propia cuenta con el flujo de código de dispositivo (RFC 8628), que solo usa
el `client_id` público y **no** ningún `client_secret`:

1. Crea la app en el portal de desarrolladores y copia su **Client ID**.
   Rellénalo en `woupi.client_id` de tu `config/config.json` (o pégalo en el
   propio asistente). Puedes dejarlo precargado en `WOUPI_CLIENT_ID`
   (`core/constants.py`), que es un valor público.
2. En la interfaz elige **Plataforma → Woupi**, define el canal (login) y
   pulsa **Cuenta Woupi** (también se abre solo al pulsar **Conectar chat**
   si todavía no hay autorización).
3. El asistente genera un código, abre el navegador en la página de
   autorización y tú la aceptas. Al terminar la app guarda los tokens en
   `config/secrets.json` (no en `config.json`).

El access token caduca a las ~4 h y se renueva solo con el refresh token. No
se comparte ninguna contraseña.

#### Opción manual: tokens en `.env`

También puedes importar los tokens a mano. Ponlos en `.env` (o en variables de
entorno); la app los migra a `config/secrets.json` en el primer arranque:

```dotenv
WOUPI_ACCESS_TOKEN=wpa_...
WOUPI_REFRESH_TOKEN=wpr_...
```

En el selector **Plataforma** elige **Woupi** y define el canal (login). El
`client_id` (público) y los endpoints van en `config/config.json`:

| Clave | Descripción |
|---|---|
| `woupi.client_id` | Client ID de tu app de Woupi (público). |
| `woupi.scopes` | Permisos pedidos al autorizar (por defecto `chat:read`). |
| `woupi.broadcaster_id` | Id del canal; si está vacío se resuelve por login. |
| `woupi.user_id` | Id del dueño del token; si está vacío se resuelve con `/oauth2/validate`. |
| `woupi.api_base_url` | Base REST (por defecto `https://api.woupi.buzz`). |
| `woupi.eventsub_url` | WebSocket de eventos (por defecto `wss://api.woupi.buzz/eventsub`). |

| Secreto (`.env` / entorno) | Descripción |
|---|---|
| `WOUPI_ACCESS_TOKEN` | Access token de usuario (`wpa_...`). |
| `WOUPI_REFRESH_TOKEN` | Refresh token (`wpr_...`); se rota solo. |
| `VPZONE_API_KEY` | API key de VPZone (opcional). |

> Los tokens (`access_token` / `refresh_token`) se guardan en texto plano en
> `config/secrets.json`, **fuera** de `config.json` y fuera del control de
> versiones. Con el flujo de dispositivo **no hay ningún secreto que proteger**.
> Si se te filtra un token, **revócalo** (ver [Seguridad](#seguridad)).

La app resuelve el `broadcaster_id` con `GET /v1/users?login=<canal>` y el
`user_id` con `POST`/`GET /oauth2/validate`, y renueva el token
automáticamente cuando caduca.

## Estructura del proyecto

```
app.py                 Punto de entrada (GUI o --headless)
.env                   Secretos locales del usuario (ignorado por git)
config/                config.json (no secreto), secrets.json (tokens) y valores por defecto
core/                  Application, eventos, config, secretos, conexión, servicios
api/                   Clientes REST/WebSocket (VPZone) y REST/EventSub (Woupi)
tts/                   Motor, cola, filtros, proveedores y audio
  providers/           piper, pyttsx3, edge, debug, fake
  filters/             Filtros de chat
  audio/               Reproducción de audio
runtime/               Sistema de plugins (contexto, ciclo de vida, loader)
plugins/               Plugins de usuario (ejemplo: debug)
gui/                   Interfaz CustomTkinter
tests/                 Scripts de prueba
logs/ temp/ audio/     Datos generados en tiempo de ejecución
voices/piper/          Modelos de voz de Piper (.onnx + .onnx.json)
```

### Añadir un proveedor TTS

Crea un archivo en `tts/providers/` que herede de `BaseProvider` y regístralo:

```python
from tts.providers.base_provider import BaseProvider
from tts.provider_factory import ProviderFactory
from tts.capabilities import Capability

class MiProvider(BaseProvider):
    name = "mio"
    def speak(self, text):
        ...

ProviderFactory.register(
    name="mio",
    provider=MiProvider,
    languages=["es"],
    priority=5,
    capabilities=[Capability.LOCAL]
)
```

### Añadir un plugin

Crea una carpeta en `plugins/` con un `plugin.json` (id, name, entry, class) y un
módulo que herede de `runtime.plugin_base.PluginBase`.

## Tests

```powershell
# Un test concreto
.\.venv\Scripts\python -m tests.test_tts

# Con pytest (si está instalado)
.\.venv\Scripts\python -m pytest
```

## Seguridad

- **Credenciales**: nunca se guardan en `config/config.json`. Los secretos viven
  en `.env` / variables de entorno y en `config/secrets.json` (ambos ignorados por
  git). No hay secretos en el código ni en `config/config.example.json` /
  `.env.example`. Si alguna vez se te filtró un token, **revócalo** en
  `POST https://api.woupi.buzz/oauth2/revoke` (parametrizado como
  `client_id` + `token`, `application/x-www-form-urlencoded`) y vuelve a
  autorizar; el token expuesto deja de ser válido de inmediato.
- **Red**: todas las APIs y websockets usan **HTTPS/WSS** (TLS verificado). No se
  desactiva la verificación de certificados.
- **Ejecución**: el código de la app no usa `eval`, `exec`, `pickle` ni
  `shell=True`. La reproducción con `ffplay` se hace con argumentos en lista.
- **Plugins**: el sistema de plugins **ejecuta código Python** que pongas en
  `plugins/`. Trátalos como código de confianza y revisa su contenido antes de
  ejecutarlos.
- **Woupi**: el acceso del usuario se hace con el **flujo de código de
  dispositivo** (app pública, solo `client_id`). La app distribuida **no lleva
  ningún `client_secret`**; cada usuario autoriza su propia cuenta desde el
  asistente y solo se guardan tokens en su `config/secrets.json`.
- **Datos temporales**: el audio se genera en `temp/` y se borra solo (al
  arrancar, periódicamente y al cerrar); el borrado está acotado a esa carpeta.

Antes de publicar en un repositorio, comprueba que **no** se incluyen
`config/config.json`, `.env` ni `config/secrets.json` (deben estar ignorados).

## Licencia

Distribuido bajo la licencia **MIT**. Consulta el archivo [`LICENSE`](LICENSE).

## Notas

- **Piper** (por defecto): funciona sin internet. Las voces se guardan en
  `voices/piper/` como `<nombre>.onnx` + `<nombre>.onnx.json`. Para añadir otra
  voz, descarga los dos ficheros desde
  <https://huggingface.co/rhasspy/piper-voices> y cópialos ahí; aparecerá sola
  en el desplegable de voces.
- **edge-tts**: Microsoft puede rechazar temporalmente el endpoint gratuito
  (error 403) según la red/IP. Si ocurre, usa **Piper** o **pyttsx3**.
- El WebSocket de VPZone (`wss://chat.vpzone.tv/ws?channel=<slug>`) puede
  responder el cierre **1008 (`bad channel`)** si el canal no existe. El canal
  debe ser el **slug** real de la plataforma, en minúsculas y de 3-32 caracteres
  (`a-z`, `0-9`, `_`, `-`). Ej.: `lordwaffl3`. La app normaliza lo que escribas
  a minúsculas; si el aviso de "bad channel" persiste, comprueba el slug.
- El audio se genera en `temp/` y se borra automáticamente tras reproducirse.
  Además, la carpeta `temp/` se vacía al **arrancar** la app, se limpia cada
  `tts.temp_clean_interval` segundos (por defecto 120) y se vuelve a vaciar al
  **cerrar**. Todo esto se activa con `tts.auto_clean_temp` (por defecto `true`),
  de forma que no quedan audios guardados entre sesiones.
