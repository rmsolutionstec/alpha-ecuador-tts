# Roadmap de Implementacion

Fecha de actualizacion: 2026-08-25

## Fase 1 - Base funcional (completada)

- [x] Motor TTS Edge y Local funcionando.
- [x] Exportacion final MP3.
- [x] Instalacion de dependencias y FFmpeg.
- [x] GUI con flujo principal (texto -> preescucha -> exportar).

## Fase 2 - Calidad de locucion (completada)

- [x] Perfiles de voz y parametros base.
- [x] Diccionario de pronunciacion por JSON.
- [x] Modo entrega y emocion.
- [x] Mastering basico con FFmpeg.
- [x] Estilos propios traducidos a ajustes reales de tono, ritmo y pausas.
- [x] Preset anti-sibilancia configurable (de-esser opcional).

## Fase 3 - Estabilidad de producto (completada)

- [x] Crear pruebas unitarias para tts.py (normalizacion, pronunciacion, tuning).
- [x] Crear pruebas de integracion minima para rutas CLI principales.
- [x] Definir textos de benchmark y validacion de calidad.
- [x] Manejo de logs de errores en archivo local sin guardar guiones.

## Fase 4 - UX de producto final (pendiente)

- [x] Separar preescucha rapida y preescucha final en GUI.
- [x] Guardado local de preferencias de usuario (ultima voz, ruta, perfil).
- [x] Historial local de renders con metadatos, sin almacenar guiones.
- [ ] Mensajes de estado con progreso mas descriptivo.

## Fase 5 - Operacion y release (pendiente)

- [x] Versionado semantico inicial: v0.2.0.
- [x] Changelog por version.
- [x] Scripts de ejecucion, pruebas y build para Windows.
- [x] Guia de QA antes de publicacion.
- [x] Licencia MIT, politica de seguridad y guia de contribucion.
- [x] Workflow de pruebas automaticas para GitHub.
- [ ] Generar un instalador y validarlo en una maquina limpia.

## Fase 6 - Comunidad y sostenibilidad

- [x] Definir modelo gratuito sostenido con donaciones voluntarias.
- [x] Preparar `.github/FUNDING.yml` sin publicar datos ficticios.
- [ ] Activar GitHub Sponsors con la cuenta real del mantenedor.
- [ ] Configurar un enlace real de apoyo en la aplicacion.

## Fase 7 - Demo web controlada

- [x] Documentar arquitectura hibrida: escritorio completo y demo limitada.
- [ ] Crear demo externa limitada a textos cortos.
- [ ] Implementar limites por sesion y limpieza de archivos temporales.
- [ ] Enlazar la demo desde Alpha Ecuador sin usar el hosting comercial como motor TTS.

## Prioridad inmediata (siguiente sprint)

1. Integrar subtítulos `.srt` con marcas de tiempo reales cuando el proveedor lo permita.
2. Instalador de Windows validado en un equipo limpio.
3. Activacion de GitHub Sponsors y publicacion inicial.
4. Demo web limitada y separada del hosting comercial.

## Auditoria tecnica 2026-05-14

- [x] Corregido bug critico: parametros manuales no quedaban aplicados cuando habia perfil activo.
- [x] Validado con pruebas A/B de velocidad y tests automatizados.
