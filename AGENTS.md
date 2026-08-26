# Guía para agentes — Alpha Studio TTS Latino

## Propósito

Alpha Studio TTS Latino es una aplicación de escritorio Windows para convertir guiones
en narraciones MP3. Alpha Ecuador es la empresa responsable y René Mejillón el
desarrollador.

## Arquitectura y compatibilidad

- `studio_tts_latino/core.py` es el motor de síntesis; no se debe acoplar a la GUI.
- `studio_tts_latino/gui.py` usa PySide6/Qt. La distribución actual mantiene Paso 1 y
  Paso 3 en la columna izquierda; Paso 2 ocupa la columna derecha completa. El Paso 3
  ofrece historial local de metadatos, generación opcional de subtítulos `.srt` y
  reproducción integrada de preescuchas.
- Conserva `studio_tts_latino` como paquete interno por compatibilidad. La marca visible
  y el ejecutable son **Alpha Studio TTS Latino** y `AlphaStudioTTSLatino.exe`.
- Las preferencias nuevas se guardan en `%LOCALAPPDATA%\AlphaStudioTTSLatino`; se leen
  las preferencias heredadas de `StudioTTSLatino` cuando las nuevas no existen.

## Calidad obligatoria

1. Antes de modificar, revisa los cambios existentes con `git status --short`.
2. Después de cambios de lógica, ejecuta:

   ```powershell
   .\.venv\Scripts\python.exe -m unittest discover -s tests -v
   ```

3. Después de cambios visuales, revisa la GUI renderizada y comprueba textos, espacios,
   scroll y controles sin recortes.
4. Para un entregable Windows, ejecuta `scripts\build_windows.ps1` y verifica
   `dist\AlphaStudioTTSLatino\AlphaStudioTTSLatino.exe`.
5. No almacenes guiones de usuario en preferencias, registros ni el repositorio.

## Cierre y repositorio

- Al terminar cada sesión de trabajo, ejecuta `git status --short`, revisa los cambios
  pendientes y confirma que no haya archivos ajenos o secretos.
- Si el usuario solicita cerrar con Git, ejecuta las pruebas pertinentes, crea un commit
  descriptivo y sube los cambios a `origin/main`; después confirma el hash y el estado
  limpio del árbol de trabajo.
- Mantén `origin` apuntando al repositorio oficial de GitHub de Alpha Ecuador.

## Documentación y mantenimiento

- Actualiza `CHANGELOG.md` y la documentación relevante cuando cambie el producto.
- Actualiza este archivo si cambian la arquitectura, dependencias, marca, distribución de
  la interfaz, pruebas requeridas o proceso de build.
- No renombres rutas internas, comandos heredados o archivos de datos sin mantener una
  ruta de compatibilidad y sus pruebas.
