# Seguridad

## Reportar una vulnerabilidad

No publiques claves, credenciales, textos privados ni datos personales en una incidencia publica.
Si encuentras un problema de seguridad, utiliza el canal de contacto disponible en
[Alpha Ecuador](https://alphaecuador.com) y describe el impacto, los pasos para reproducirlo
y la version afectada.

## Alcance

- El proveedor `edge` envia el texto al servicio externo utilizado por `edge-tts`.
- El proveedor `local` procesa el texto en el equipo y requiere FFmpeg para exportar MP3.
- Las preferencias y registros tecnicos se guardan fuera del repositorio.
- Los textos escritos por el usuario no deben incorporarse a registros, capturas ni pruebas.
- Ninguna credencial debe almacenarse en el codigo, el historial de Git o los archivos de ejemplo.
- Las versiones web futuras deben usar limites de uso y una infraestructura separada del hosting comercial.

Consulta [Seguridad y privacidad](docs/seguridad-y-privacidad.md) para las medidas completas.
