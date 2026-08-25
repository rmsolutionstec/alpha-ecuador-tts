# Contribuir a Studio TTS Latino

Gracias por ayudar a mantener un proyecto gratuito, abierto y util para la comunidad.

## Preparar el entorno

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Antes de enviar cambios

1. Mantiene la compatibilidad de `python gui.py` y `python tts.py`.
2. Agrega o actualiza pruebas para cada correccion.
3. Ejecuta `python -m unittest discover -s tests -v`.
4. Actualiza la documentacion y `CHANGELOG.md` cuando corresponda.
5. No publiques audios personales, credenciales, entornos virtuales o archivos temporales.
6. Explica claramente las limitaciones de los proveedores externos.

## Estructura

- `studio_tts_latino/`: codigo de la aplicacion.
- `tests/`: pruebas automatizadas.
- `docs/`: documentacion del producto y operacion.
- `examples/`: muestras seguras para pruebas manuales.
- `scripts/`: herramientas de desarrollo y empaquetado.

## Licencia

Las contribuciones al codigo propio del proyecto se publican bajo la licencia MIT.
Las dependencias de terceros conservan sus propias condiciones.
