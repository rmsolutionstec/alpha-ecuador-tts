# Alpha Studio TTS Latino

Aplicacion gratuita y de codigo abierto para convertir guiones en narraciones MP3 con
voces en espanol latino. Es un producto de **Alpha Ecuador**, desarrollado por
**René Mejillón**, y se mantiene como herramienta comunitaria con apoyo voluntario.

> Estado: beta `0.2.0` · Plataforma principal: Windows · Licencia: MIT

## Créditos

- Empresa y responsable del proyecto: **Alpha Ecuador**.
- Desarrollador: **René Mejillón**.
- Sitio web: [alphaecuador.com](https://alphaecuador.com).

## Que ofrece

- Voces latinas en linea mediante Edge TTS.
- Proveedor local para trabajar sin internet, segun las voces instaladas en el equipo.
- Perfiles de locucion para noticias, documentales, anuncios y narraciones.
- Ajustes reales de ritmo, tono, emocion y pausas orientativas.
- Diccionario personalizable para siglas, marcas y palabras dificiles.
- Exportacion MP3 y mastering opcional con FFmpeg.
- Generacion opcional de subtitulos `.srt` por frases junto al MP3.
- Preescucha rapida y preescucha final.
- Reproduccion integrada de la ultima preescucha dentro de la ventana.
- Historial local de renders con metadatos, sin guardar guiones.
- Preferencias locales, mensajes de estado y pruebas automatizadas.
- Interfaz de escritorio y linea de comandos.

## Inicio rapido

Requisitos: Python 3.10 o superior y Windows. FFmpeg es recomendable para mastering y
necesario cuando se utiliza el proveedor local con salida MP3.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python gui.py
```

Tambien puedes iniciar la aplicacion con:

```powershell
.\scripts\run_gui.ps1
```

## Generar audio por terminal

```powershell
python tts.py --text "Hola, bienvenido a Alpha Studio TTS Latino" --provider edge --output saludo.mp3
```

```powershell
python tts.py --file examples/guion-informativo.txt --profile documental --emotion calido --output documental.mp3
```

```powershell
python -m studio_tts_latino --help
```

Para un diccionario personalizado:

```powershell
python tts.py --text "Alpha Ecuador y OpenAI" --pronunciation-file examples/pronunciacion-personalizada.json --output ejemplo.mp3
```

## Estructura del proyecto

```text
alpha-studio-tts-latino/
├── studio_tts_latino/
│   ├── core.py                 Motor de sintesis y audio
│   ├── cli.py                  Interfaz de comandos
│   ├── gui.py                  Aplicacion de escritorio
│   ├── settings.py             Preferencias y registros locales
│   ├── subtitles.py            Generacion opcional de archivos SRT
│   └── data/                   Recursos incluidos
├── docs/                       Documentacion de producto y operacion
├── examples/                   Guiones y diccionarios de ejemplo
├── scripts/                    Ejecucion, pruebas y empaquetado
├── tests/                      Pruebas automatizadas
├── .github/                    Integracion continua y patrocinio
├── gui.py                      Lanzador compatible
├── tts.py                      Lanzador CLI compatible
└── pyproject.toml              Configuracion del paquete
```

## Documentacion

- [Instalacion y requisitos](docs/instalacion.md).
- [Uso de la aplicacion y la CLI](docs/uso.md).
- [Arquitectura del proyecto](docs/arquitectura.md).
- [Guia de locucion profesional](docs/guia-locucion.md).
- [Seguridad y privacidad](docs/seguridad-y-privacidad.md).
- [Modelo gratuito y donaciones](docs/modelo-comunitario.md).
- [Estrategia de demo web y Alpha Ecuador](docs/estrategia-web.md).
- [Estado actual del producto](docs/estado-del-producto.md).
- [Hoja de ruta](docs/hoja-de-ruta.md).
- [Checklist de lanzamiento](docs/checklist-lanzamiento.md).
- [Textos de validacion](docs/benchmarks.md).
- [Historial de cambios](CHANGELOG.md).
- [Créditos y atribución](AUTHORS.md).

## Probar el proyecto

```powershell
python -m unittest discover -s tests -v
```

```powershell
.\scripts\run_tests.ps1
```

## Preparar un ejecutable de Windows

```powershell
python -m pip install ".[build]"
.\scripts\build_windows.ps1
```

El resultado se crea en `dist/AlphaStudioTTSLatino`. FFmpeg no se incluye automaticamente;
debe instalarse por separado cuando el usuario necesite mastering o el proveedor local.

## Privacidad y limites

- `edge` requiere internet y envia el texto al servicio externo usado por `edge-tts`.
- `local` utiliza las voces disponibles en el equipo y no requiere internet para sintetizar.
- La aplicacion no debe almacenar guiones en registros tecnicos.
- Las pausas expresadas en milisegundos son orientativas: Edge no permite definir silencios
  SSML arbitrarios en este flujo.
- Los subtitulos SRT se generan por frases usando la duracion real del audio cuando `ffprobe`
  esta disponible; si no, se usa una estimacion basada en palabras por minuto.
- Los audios, entornos virtuales, secretos y configuraciones privadas se excluyen del repositorio.

## Apoyar el proyecto

El software y sus funciones siguen siendo gratuitos. Las donaciones son completamente
voluntarias y se activaran mediante GitHub Sponsors o un enlace real configurado por
Alpha Ecuador.

Para personalizar el boton de la aplicacion:

```powershell
$env:STUDIO_TTS_DONATION_URL = "https://tu-enlace-real-de-apoyo"
python gui.py
```

Consulta [Modelo comunitario](docs/modelo-comunitario.md) antes de configurar el
patrocinio. No se incluyen cuentas, enlaces de pago ni credenciales ficticias.

## Licencia

El codigo propio del proyecto se distribuye bajo licencia [MIT](LICENSE). Las
dependencias externas conservan sus respectivas licencias.
