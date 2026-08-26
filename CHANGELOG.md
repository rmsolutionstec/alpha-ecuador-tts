# Historial de cambios

Este archivo registra cambios importantes del proyecto.

## Pendiente de publicación

### Cambiado

- El Paso 3 permite crear opcionalmente un archivo `.srt` junto al MP3, dividido por
  frases y distribuido sobre la duración del audio.
- El Paso 3 incorpora un historial local de los últimos renders con fecha, archivo y
  parámetros básicos; nunca se guarda el texto del guion.
- La interfaz de escritorio migra de Tkinter a PySide6/Qt, con jerarquía visual,
  tarjetas, controles de voz agrupados y una acción de exportación destacada.
- La configuración avanzada se concentra en una sección desplegable para simplificar
  el flujo principal de guion, voz y exportación.
- Se añadieron contador de palabras/caracteres y mensajes de estado visuales.
- Cambio de marca visible a **Alpha Studio TTS Latino**, incluido el ejecutable
  `AlphaStudioTTSLatino.exe`, los comandos nuevos y la carpeta local de preferencias.
- Paso 3 se movió a la parte inferior izquierda y Paso 2 ocupa toda la columna derecha.

### Corregido

- La conversión local a MP3 indica explícitamente el formato a FFmpeg aunque el archivo
  temporal use la extensión interna `.part`.
- Las preescuchas se reproducen dentro de la aplicación y ya no dependen de un reproductor
  externo del sistema.
- El texto de los ajustes avanzados ya no se recorta en la interfaz de Windows.

## 0.2.0 - 2026-08-25

### Agregado

- Créditos visibles de Alpha Ecuador como empresa responsable y René Mejillón como desarrollador.
- Paquete Python `studio_tts_latino` con motor, CLI, GUI y preferencias separadas.
- Configuracion de proyecto con `pyproject.toml`, licencia MIT y reglas `.gitignore`.
- Documentacion de arquitectura, privacidad, modelo comunitario y futura demo web.
- Persistencia local de preferencias y registro tecnico fuera del repositorio.
- Enlace configurable para apoyar el proyecto desde la aplicacion de escritorio.
- Scripts para ejecutar la GUI, correr pruebas y preparar un build de Windows.
- Workflow de GitHub Actions y configuracion inicial de patrocinio.
- Cobertura ampliada para voces, pausas, estilos, errores de CLI y preferencias.

### Cambiado

- Diccionario de pronunciacion movido a los recursos internos del paquete.
- Documentacion historica organizada en la carpeta `docs/`.
- Preescucha temporal movida fuera de la carpeta del proyecto.
- Estilos de locucion convertidos en ajustes reales de ritmo, tono y pausas.
- Las pruebas de audio usan nombres temporales unicos y se limpian al finalizar.

### Corregido

- La voz elegida ahora tiene prioridad sobre la preferencia de genero.
- Las pausas entre frases ya no duplican la puntuacion.
- Los errores de la GUI conservan correctamente el mensaje de excepcion.
- Los archivos de entrada inexistentes muestran errores claros sin traceback.
- Las voces locales con idiomas expresados como bytes ya no producen errores.
- La deteccion de voces masculinas ya no clasifica `female` como `male`.
- Las preescuchas rapida y final ya pueden generarse en paralelo sin compartir archivos.

### Seguridad

- Escritura atomica de audio y preferencias para evitar archivos incompletos.
- Validacion del motor para los parametros de voz, formato, perfil y mastering,
  incluso fuera de la CLI o GUI.
- Archivos temporales unicos para sintesis, conversion local y mastering.
- Exclusiones de secretos, entornos virtuales, audios y artefactos de build.
- Definicion de privacidad para textos enviados a proveedores externos.

## 0.1.0 - 2026-05-14

### Agregado

- Estructura GUI tipo estudio para flujo de locucion.
- Perfiles de voz en espanol latino.
- Modo de entrega y emocion para ajuste de locucion.
- Diccionario JSON de pronunciacion.
- Documentacion de uso y guia de locutor.
- Deteccion robusta de FFmpeg para entorno Windows.
- Visualizacion numerica de sliders en GUI.
- Doble preescucha en GUI: rapida 5s y final.
- Presets de mastering seleccionables (suave, anti-sibilancia, voz-profunda).
- Tests unitarios e integracion minima en carpeta tests.
- Checklist QA de release y textos benchmark de validacion.

### Cambiado

- Exportacion final normalizada a MP3.
- Preescucha alineada con pipeline de calidad final.
- Cadena de mastering ajustada a un perfil mas suave para voz.

### Corregido

- Error de dependencias faltantes en primer arranque.
- Inconsistencias de formato entre proveedores.
- Problema de artefactos/chillido por pipeline previo.
- Error critico donde el perfil sobrescribia ajustes manuales (rate, volumen, pausa, estilo), haciendo que muchos cambios sonaran igual.

## Proximas mejoras

- Historial local de renders sin almacenar textos sensibles.
- Generacion opcional de subtitulos `.srt`.
- Instalador de Windows validado en una maquina limpia.
- Demo web limitada y alojada fuera del hosting comercial.
