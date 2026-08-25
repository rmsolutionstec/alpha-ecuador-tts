# Estrategia web sin sobrecargar Alpha Ecuador

## Decision actual

La aplicacion de escritorio es el producto principal. Una futura demo web solo debe
permitir probar el proyecto; no debe convertirse en un generador ilimitado de audio.

## Arquitectura recomendada

```text
alphaecuador.com
    Sitio comercial, descripcion del proyecto y enlaces.

GitHub
    Codigo fuente, documentacion, instaladores y patrocinios.

Proveedor externo de demo
    Aplicacion web limitada, independiente del hosting comercial.

Computador del usuario
    Aplicacion completa de escritorio.
```

## Subdominios

Se puede reservar un nombre como `tts.alphaecuador.com`, pero un subdominio no crea
recursos separados. Si apunta al mismo hosting compartido, consume la misma CPU, RAM,
espacio y capacidad de transferencia que el sitio comercial.

Solo debe configurarse cuando el proveedor externo admita dominios personalizados o
cuando exista un servidor independiente preparado para gestionarlo.

## Demo gratuita inicial

Una demo externa puede ofrecer:

- Maximo de 300 a 500 caracteres por generacion.
- Un numero limitado de generaciones por sesion.
- Pocas voces y perfiles basicos.
- Descarga de un unico archivo MP3.
- Enlace al instalador completo y a la pagina de patrocinio.
- Limpieza de archivos temporales.

Las plataformas gratuitas pueden usar su propio dominio. En ese caso, Alpha Ecuador
solo necesita enlazar o incrustar la demo, cuando el proveedor lo permita.

## Cuando escalar

Considera un servidor dedicado solo si el uso, los patrocinios o las necesidades de
operacion justifican el gasto. La prioridad es que la generacion de audio no afecte el
sitio utilizado para ofrecer servicios web.
