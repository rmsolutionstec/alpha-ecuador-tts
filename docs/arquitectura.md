# Arquitectura

## Principio general

Alpha Studio TTS Latino es una aplicacion de escritorio gratuita. El motor se mantiene
independiente de la interfaz para facilitar pruebas, automatizacion y una futura demo web.

```text
gui.py ──► studio_tts_latino.gui ──┐
                                  ├──► studio_tts_latino.core ──► Edge / voces locales
tts.py ──► studio_tts_latino.cli ──┘                │
                                                    └──► FFmpeg opcional
```

## Componentes

`studio_tts_latino/core.py` concentra perfiles, validacion, seleccion de voces,
normalizacion de texto, sintesis y mastering.

`studio_tts_latino/cli.py` valida argumentos y presenta mensajes claros para errores
de archivos, valores invalidos y problemas de generacion.

`studio_tts_latino/gui.py` contiene la interfaz moderna basada en PySide6/Qt. Ejecuta
la sintesis en hilos de trabajo y vuelve al hilo principal mediante señales Qt para
actualizar el progreso, los mensajes y la reproducción de preescuchas con seguridad.

`studio_tts_latino/settings.py` guarda preferencias y registros fuera del repositorio.

`studio_tts_latino/data/` contiene el diccionario de pronunciacion incluido en el paquete.

## Datos locales

En Windows, preferencias y registros se guardan bajo:

```text
%LOCALAPPDATA%\AlphaStudioTTSLatino\
├── preferences.json
└── logs\alpha-studio-tts-latino.log
```

No se guardan los guiones escritos por el usuario en preferencias ni registros.

## Compatibilidad

Los lanzadores `python gui.py` y `python tts.py` permanecen en la raiz para evitar
romper instrucciones anteriores o integraciones existentes.

Tambien se admite:

```powershell
python -m studio_tts_latino --help
```

## Futuro despliegue web

La demo web debe reutilizar el motor, limitar entradas y ejecutarse en una infraestructura
independiente del sitio comercial `alphaecuador.com`. Consulta
[Estrategia web](estrategia-web.md).
