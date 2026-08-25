# Uso de Alpha Studio TTS Latino

## Aplicacion de escritorio

1. Ejecuta `python gui.py`.
2. Escribe o carga un guion de texto.
3. Selecciona un perfil y una voz.
4. Ajusta velocidad, volumen, estilo, emocion y pausas.
5. Usa la preescucha rapida o final.
6. Elige una ruta y exporta el MP3.

La aplicacion guarda preferencias de voz y configuracion en la carpeta de datos local
del usuario. El texto escrito no forma parte de esas preferencias.

## Proveedores

### Edge

- Mejor naturalidad para voces latinas.
- Requiere conexion a internet.
- El texto se envia a un servicio externo.
- Permite ajustar ritmo, tono y volumen.

### Local

- Usa las voces instaladas en el sistema.
- No requiere internet para sintetizar.
- Necesita FFmpeg para exportar MP3.
- La calidad depende de las voces disponibles en el equipo.

## Ejemplos de CLI

```powershell
python tts.py --text "Buenas noches" --profile locutor-latino --output noticia.mp3
```

```powershell
python tts.py --file examples/guion-informativo.txt --profile documental --emotion calido --output documental.mp3
```

```powershell
python tts.py --text "Promocion especial" --profile comercial-energetico --delivery-mode comercial --output anuncio.mp3
```

```powershell
python tts.py --text "Audio sin postproceso" --no-mastering --output directo.mp3
```

```powershell
python tts.py --text "Alpha Ecuador" --pronunciation-file examples/pronunciacion-personalizada.json --output marca.mp3
```

## Estilos y pausas

Los estilos se convierten en ajustes reales de velocidad, tono y puntuacion. No son
estilos SSML oficiales de Microsoft. Las pausas son orientativas y no garantizan una
duracion exacta en milisegundos.

## Preescucha

La preescucha rapida utiliza un fragmento corto del guion. No promete una duracion
fija. Los archivos de preescucha se crean en el directorio temporal del sistema.

## Apoyo voluntario

El boton `Apoyar el proyecto` abre el sitio institucional por defecto. Puedes cambiar
el destino configurando `STUDIO_TTS_DONATION_URL` con un enlace real de patrocinio.
