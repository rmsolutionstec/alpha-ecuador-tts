# Seguridad y privacidad

## Clasificacion de datos

- Los guiones pueden contener datos personales, mensajes comerciales o informacion privada.
- Las rutas locales y preferencias pueden revelar nombres de usuario o estructura de archivos.
- Los audios generados son documentos de trabajo y no deben publicarse automaticamente.

## Proveedor Edge

El proveedor `edge` necesita internet y transmite el texto al servicio externo usado por
`edge-tts`. No utilices este proveedor con informacion confidencial sin evaluar primero
las condiciones del servicio correspondiente.

## Proveedor local

El proveedor `local` utiliza las voces disponibles en el equipo. Es la opcion preferible
cuando el texto no debe enviarse a un servicio externo.

## Medidas implementadas

- El repositorio excluye entornos virtuales, secretos, configuraciones privadas y audios.
- Los registros tecnicos se guardan fuera del proyecto.
- Las preferencias no incluyen el texto del usuario.
- Los archivos de salida se escriben de manera atomica cuando el proveedor Edge finaliza.
- La preescucha usa el directorio temporal del sistema.
- Los mensajes de error evitan exponer trazas tecnicas innecesarias en la CLI.

## Antes de publicar

1. Revisa `git status` y `git diff`.
2. Comprueba que no existan tokens, claves, audios privados ni datos de clientes.
3. No agregues `.venv/`, `dist/`, `build/` o carpetas de registros.
4. Comprueba las licencias de `edge-tts`, `pyttsx3`, FFmpeg y cualquier voz adicional.
5. Activa autenticacion de dos factores en GitHub.

## Futuras versiones web

- Limitar texto, frecuencia y concurrencia.
- Eliminar archivos temporales al finalizar.
- No conservar guiones sin consentimiento.
- Separar el motor del hosting comercial de Alpha Ecuador.
- Mostrar claramente que el proveedor Edge utiliza un tercero.
