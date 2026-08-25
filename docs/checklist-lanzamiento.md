# Checklist de lanzamiento

Usar este checklist antes de marcar una version como estable.

## 1) Setup limpio

- [ ] Crear entorno virtual nuevo.
- [ ] Instalar dependencias con requirements.txt.
- [ ] Verificar FFmpeg disponible.

## 2) Pruebas automaticas

- [ ] Ejecutar tests unitarios e integracion minima.
- [ ] Confirmar cero fallos.

## 3) Validacion funcional GUI

- [ ] Abrir app sin errores.
- [ ] Preescucha rapida funciona.
- [ ] Preescucha final funciona.
- [ ] Exportacion MP3 funciona.
- [ ] Sliders muestran valores numericos correctos.

## 4) Validacion de audio

- [ ] Render con preset suave sin artefactos.
- [ ] Render con preset anti-sibilancia validado.
- [ ] Pronunciacion personalizada aplicada desde JSON.

## 5) CLI minima

- [ ] Comando --help responde correctamente.
- [ ] Comando sin --text/--file falla con mensaje claro.
- [ ] Render edge exitoso con profile locutor-latino.

## 6) Documentacion

- [ ] README actualizado con comandos vigentes.
- [ ] Roadmap actualizado segun estado real.
- [ ] Changelog actualizado con cambios de release.
- [ ] `.gitignore` excluye entornos, audios y secretos.
- [ ] La licencia y los avisos de privacidad estan disponibles.
- [ ] El enlace de patrocinio no apunta a una cuenta ficticia.
