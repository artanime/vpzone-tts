# Voces de Piper

Modelos de voz neuronales **offline** para el proveedor Piper. No requieren
internet ni Microsoft Edge: la sintesis ocurre en local con ONNX Runtime.

## Como se instalan

Las voces **no** se suben a este repositorio (los `.onnx` pesan ~60 MB cada uno).
Se descargan con el script incluido, que no necesita Python ni la app instalada:

```powershell
# Ver el catalogo completo con licencias
powershell -ExecutionPolicy Bypass -File .\voices\instalar_voces.ps1 -Listar

# Instalar todas las voces de licencia libre (recomendado)
powershell -ExecutionPolicy Bypass -File .\voices\instalar_voces.ps1 -Publicas

# Instalar voces concretas
powershell -ExecutionPolicy Bypass -File .\voices\instalar_voces.ps1 -Voz en_US-amy-medium, fr_FR-siwis-medium

# Reinstalar una voz
powershell -ExecutionPolicy Bypass -File .\voices\instalar_voces.ps1 -Voz en_US-joe-medium -Forzar

# Comprobar que las voces instaladas no se han alterado
powershell -ExecutionPolicy Bypass -File .\voices\instalar_voces.ps1 -Verificar
```

> Si PowerShell bloquea la ejecucion de scripts, el `Bypass` de arriba lo
> resuelve. Tambien vale `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

### Verificacion de integridad (SHA-256)

Cada descarga se comprueba contra el **SHA-256 oficial** del modelo y de su
`.onnx.json`, ademas del tamano exacto:

- Se descarga a un fichero temporal `.part`; solo se mueve a su sitio cuando el
  hash coincide. Si no coincide, el `.part` se borra y **no queda ningun fichero
  sin verificar** en la carpeta.
- Si un modelo instalado se ha corrompido o modificado, `-Verificar` lo detecta
  y una nueva ejecucion del script lo vuelve a descargar.
- Solo se aceptan descargas por HTTPS que terminen en un host de HuggingFace; si
  la redireccion acaba en otro dominio, se aborta.
- Los modelos se tratan como datos: el script nunca los ejecuta.

El SHA-256 de los modelos es el que publica HuggingFace (LFS); el de los
`.onnx.json` se fijo a partir del fichero publicado. Si HuggingFace actualiza un
modelo, la descarga fallara a proposito hasta que se actualice la tabla de
huellas del script (es lo que evita que un cambio silencioso pase inadvertido).

Los ficheros se guardan en `voices/piper/` y **aparecen automaticamente** en el
desplegable de voces de la app: no hay que tocar `config/config.json`.

Cada voz son dos ficheros:

```
voices/piper/<nombre>.onnx        modelo
voices/piper/<nombre>.onnx.json   configuracion (fonemas, sample rate, hablantes)
```

### Descarga manual

Si prefieres bajar los ficheros a mano, estan en
[Hugging Face](https://huggingface.co/rhasspy/piper-voices). La ruta de cada
voz es `<familia>/<codigo>/<nombre>/<calidad>/<nombre-completo>.onnx`, por
ejemplo:

```
https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx
https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json
```

## Voces disponibles

### Redistribuibles (dominio publico, CC0, Apache-2.0, CC BY, CC BY-SA, AGPL-3.0)

| Voz | Idioma | Tamano | Licencia | Notas |
|---|---|---|---|---|
| `es_ES-davefx-medium` | Espanol (ES) | 60,3 MB | CC0 | Voz por defecto de la app |
| `es_ES-sharvard-medium` | Espanol (ES) | 73,2 MB | CC BY 3.0 | Espanol (ES) |
| `en_US-amy-medium` | Ingles (US) | 60,3 MB | CC BY-SA 4.0 | Femenina |
| `en_US-joe-medium` | Ingles (US) | 60,3 MB | CC0 | Masculina |
| `en_US-mike-medium` | Ingles (US) | 60,3 MB | CC0 | Masculina |
| `en_US-sam-medium` | Ingles (US) | 60,0 MB | Apache-2.0 | No binaria |
| `en_US-kristin-medium` | Ingles (US) | 60,6 MB | Dominio publico | Femenina |
| `en_US-john-medium` | Ingles (US) | 60,6 MB | Dominio publico | Masculina |
| `en_US-bryce-medium` | Ingles (US) | 60,6 MB | Dominio publico | Masculina |
| `en_US-norman-medium` | Ingles (US) | 60,6 MB | Dominio publico | Masculina |
| `en_US-ljspeech-medium` | Ingles (US) | 60,6 MB | Dominio publico | LJSpeech |
| `en_GB-cori-medium` | Ingles (GB) | 60,6 MB | Dominio publico | Femenina |
| `en_GB-alba-medium` | Ingles (GB) | 60,3 MB | CC BY 4.0 | Femenina |
| `en_GB-alan-medium` | Ingles (GB) | 60,3 MB | CC BY-SA 4.0 | Masculina |
| `fr_FR-siwis-medium` | Frances | 60,3 MB | CC BY 4.0 | Masculina |
| `fr_FR-upmc-medium` | Frances | 73,2 MB | CC BY-SA 4.0 | 2 hablantes |
| `fr_FR-tom-medium` | Frances | 60,6 MB | AGPL-3.0 | Masculina, 44,1 kHz |
| `fr_FR-gilles-low` | Frances | 60,2 MB | CC0 | Masculina, calidad baja |
| `fr_FR-mls_1840-low` | Frances | 60,2 MB | CC BY 4.0 | Masculina, 1840 |
| `fr_FR-mls-medium` | Frances | 73,2 MB | CC BY 4.0 | 125 hablantes |

### Uso restringido (instalacion personal, no redistribuir)

Estas voces tienen datasets **no comerciales** o de **uso restringido**.
El script las omite en `-Publicas`; solo se instalan pidiendolas por nombre o
con `-Todas`. No las publiques ni las incluyas en releases del repo.

| Voz | Idioma | Tamano | Licencia | Nota |
|---|---|---|---|---|
| `en_US-ryan-medium` | Ingles (US) | 60,3 MB | CC BY-NC-SA 4.0 | No comercial |
| `en_US-kusal-medium` | Ingles (US) | 60,3 MB | CC BY-NC-SA 4.0 | No comercial |
| `en_US-hfc_female-medium` | Ingles (US) | 60,3 MB | CC BY-NC-SA 4.0 | No comercial |
| `en_US-hfc_male-medium` | Ingles (US) | 60,3 MB | CC BY-NC-SA 4.0 | No comercial |
| `en_US-lessac-medium` | Ingles (US) | 60,3 MB | Blizzard 2013 | Solo investigacion |
| `en_GB-semaine-medium` | Ingles (GB) | 73,2 MB | CC BY-NC-SA 4.0 | No comercial |

## Sobre las licencias

Cada modelo de voz se entrena con un dataset distinto y **hereda su licencia**.
El script y esta tabla se basan en la ficha del modelo en
[Hugging Face](https://huggingface.co/rhasspy/piper-voices/tree/main), donde
puedes ver el dataset de origen de cada voz.

El codigo de VPZone TTS es MIT, pero **eso no cambia la licencia de los
modelos**. Si vas a redistribuir voces, incluye la atribucion (dataset + licencia)
y respeta las condiciones de la licencia: CC BY exige creditos, CC BY-SA exige
compartir bajo la misma licencia, y las licencias **NC** (no comercial) y las de
investigacion **no** permiten redistribucion libre.

El codigo de Piper es MIT: <https://github.com/rhasspy/piper>.

## Añadir una voz que no este en el catalogo

Cualquier voz del repositorio de Piper funciona, aunque no este en la lista.
Descarga los dos ficheros a `voices/piper/` con el nombre `<nombre>.onnx` y
`<nombre>.onnx.json` y aparecera en el desplegable. El idioma se deduce del
prefijo del nombre (`en_US-...`, `fr_FR-...`, `es_ES-...`).

Esa voz descargada a mano **no tendra SHA-256 verificado**: `-Verificar` la
mostrara como "no catalogada". Si quieres que el script la verifique, anade una
linea en `$Catalogo` y su huella en `$Huellas` (el `sha256` del `.onnx` esta en
la ficha del fichero en HuggingFace, dentro de `lfs.oid`).
