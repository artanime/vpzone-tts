# Política de seguridad

## Versiones soportadas

Solo se da soporte de seguridad a la última versión publicada en la rama `main`.

| Versión | Soportada |
|---|---|
| `main` (última) | Sí |
| Anteriores | No |

## Cómo reportar una vulnerabilidad

**No abras un issue público.** Usa el reporte privado de GitHub:

<https://github.com/artanime/vpzone-tts/security/advisories/new>

Incluye, si puedes:

- Versión o commit afectado.
- Pasos para reproducirlo.
- Impacto que crees que tiene (ej. ejecución de código, fuga de datos, DoS).
- Versión de Python y de Windows.

Plazo orientativo de respuesta: **7 días** para acusar recibo y **30 días** para
publicar un parche si se confirma. Si el fallo afecta a una dependencia de
terceros, se abrirá un PR de actualización y se te mencionará en el aviso.

## Alcance

Este proyecto es una aplicación de escritorio que se conecta a servicios de
terceros. Quedan **dentro** del alcance:

- El código de `core/`, `api/`, `tts/`, `gui/` y `runtime/`.
- La gestión de secretos (`.env`, `config/secrets.json`) y su fuga accidental.
- La descarga y validación de modelos de voz (`voices/`).
- Las dependencias fijadas en `requirements.txt`.

Quedan **fuera** del alcance:

- Vulnerabilidades en las APIs de VPZone o Woupi.
- Fallos del propio Windows, Python o de las voces de Piper.
- Ataques que requieran control físico del equipo o permisos de administrador.
- Ingeniería social.

## Medidas ya aplicadas

- Dependencias fijadas con `==` y auditadas contra la base de datos de OSV;
  última revisión: **2026-11-09**, sin avisos abiertos.
- **Dependabot** configurado (`.github/dependabot.yml`) para abrir PRs semanales
  de actualización y de avisos de seguridad.
- **Auditoría automática** con `pip-audit` en cada push y PR
  (`.github/workflows/security.yml`).
- Los secretos locales (`config/config.json`, `.env`, `config/secrets.json`) y
  los modelos descargados (`voices/**/*.onnx*`) están en `.gitignore`.
- Las voces que se redistribuyen en el release tienen licencia compatible; las
  de uso restringido o no comercial no se publican.

## Buenas prácticas para quien use el proyecto

- No subas nunca `config/config.json`, `.env` ni `config/secrets.json`.
- Usa un token de GitHub de **permisos mínimos** y revócalo al terminar.
- Ejecuta `python -m pip_audit` tras actualizar dependencias.
- Descarga las voces solo desde `huggingface.co/rhasspy/piper-voices` o desde el
  release oficial de este repositorio.
