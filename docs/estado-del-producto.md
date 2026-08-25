# Estado del Producto - Alpha Studio TTS Latino

Fecha de corte: 2026-08-25

## Objetivo del producto

Construir una aplicacion de texto a voz en espanol latino con calidad de locutor, flujo profesional y exportacion final en MP3.

## Estado actual (resumen ejecutivo)

- Estado general: Beta publica preparada para evolucionar como proyecto comunitario.
- Motor TTS: Funcional y usable en produccion basica.
- Interfaz GUI: Moderna en PySide6, con guion y exportación a la izquierda, y controles
  completos de voz en la columna derecha.
- Calidad de audio: Buena, con mastering opcional via FFmpeg.
- Documentacion: Centralizada en `docs/`, con arquitectura, privacidad y estrategia de despliegue.

## Funcionalidades implementadas

- Exportacion final en MP3.
- Proveedor Edge como flujo recomendado.
- Soporte proveedor local con conversion a MP3.
- Deteccion robusta de FFmpeg en Windows.
- Perfiles de locucion predefinidos.
- Modos de entrega (noticia, documental, comercial, podcast).
- Emocion (neutro, serio, calido, energetico).
- Diccionario de pronunciacion JSON.
- Preescucha desde GUI.
- Ajuste visual de sliders con valor numerico visible.
- Manejo de errores de ejecucion con mensajes claros.
- Persistencia local de preferencias sin almacenar el texto del usuario.
- Registros tecnicos fuera del repositorio.
- Compatibilidad con lanzadores historicos y paquete Python instalable.
- Pruebas automatizadas para motor, CLI y preferencias.

## Riesgos y limitaciones actuales

- Los estilos de voz se simulan mediante ajustes reales de ritmo, tono y pausas; no usan SSML personalizado.
- Las pausas expresadas en milisegundos son orientativas porque Edge no garantiza silencios exactos.
- El proveedor Edge depende de internet y de un servicio externo.
- El instalador para Windows tiene un script base, pero requiere instalar PyInstaller y validarse en una maquina limpia.
- La demo web aun no existe y, cuando se construya, debe estar aislada del hosting comercial.

## Criterio de salida a producto final (v1.0)

- Flujo GUI estable sin regresiones en preescucha y render.
- Calidad de audio consistente en al menos 20 textos de prueba.
- Suite minima de pruebas automatizadas pasando en local.
- Guia de instalacion y uso completa validada desde cero.
- Checklist de release y changelog actualizados.

## Metricas sugeridas para aceptar calidad

- Tiempo de render por minuto de texto (objetivo: aceptable para uso diario).
- Reintentos por error de generacion (objetivo: < 3%).
- Numero de correcciones manuales de pronunciacion por guion (objetivo: decreciente).
- Satisfaccion subjetiva de audio (escala interna 1-5, objetivo >= 4).
