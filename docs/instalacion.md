# Instalacion

## Requisitos

- Windows 10 u 11.
- Python 3.10 o superior.
- Conexion a internet para voces Edge.
- FFmpeg para mastering y para convertir la salida local a MP3.

## Crear el entorno

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell no permite activar el entorno, ejecuta directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe gui.py
```

## Verificar FFmpeg

```powershell
ffmpeg -version
```

Si FFmpeg no esta instalado, la aplicacion puede generar MP3 mediante Edge, pero no
aplicara mastering. El proveedor local necesita FFmpeg para convertir WAV a MP3.

## Iniciar la aplicacion

```powershell
python gui.py
```

Alternativa:

```powershell
.\scripts\run_gui.ps1
```

## Instalar el paquete localmente

```powershell
python -m pip install -e .
studio-tts --help
```

## Preparar un ejecutable

```powershell
python -m pip install ".[build]"
.\scripts\build_windows.ps1
```

Verifica el ejecutable en otro equipo antes de distribuirlo. Los directorios `build/`
y `dist/` se generan localmente y no deben agregarse al repositorio.
