# Guia de Locucion Profesional (Studio TTS Latino)

Esta guia resume como sonar mas humano y menos sintetico.

## 1) Configuracion recomendada base

- Proveedor: `edge`
- Perfil: `locutor-latino`
- Modo natural: activado
- Modo de entrega: `noticia` o `podcast` segun contenido
- Emocion: `serio` para informativo, `calido` para narrativo
- Mastering: activado
- Salida: MP3 192 kbps

## 2) Cuadros rapidos por tipo de proyecto

### Narracion corporativa

- Perfil: `locutor-latino`
- Modo de entrega: `podcast`
- Emocion: `serio`
- Pausas recomendadas: 220-300 ms

### Documental

- Perfil: `documental`
- Modo de entrega: `documental`
- Emocion: `calido`
- Pausas recomendadas: 320-460 ms

### Comercial

- Perfil: `comercial-energetico`
- Modo de entrega: `comercial`
- Emocion: `energetico`
- Pausas recomendadas: 120-220 ms

## 3) Buenas practicas de guion

- Escribe una idea por frase.
- Mantiene frases entre 10 y 18 palabras.
- Usa comas donde un locutor respiraria.
- Evita bloques largos sin puntos.
- Si hay siglas o marcas, define pronunciacion en el diccionario JSON.

## 4) Diccionario de pronunciacion

Por defecto se usa `studio_tts_latino/data/pronunciation_es_mx.json`.

Formato:

```json
{
  "palabra_original": "como_debe_sonar"
}
```

Ejemplo:

```json
{
  "OpenAI": "open ei ai",
  "SQL": "sequel"
}
```

## 5) Flujo profesional sugerido

1. Cargar texto.
2. Elegir perfil y modo de entrega.
3. Seleccionar emocion.
4. Ejecutar una preescucha rapida.
5. Ajustar pausas y voz.
6. Exportar MP3 final.
7. Reescuchar y hacer una segunda version con pequenos cambios.

## 6) Checklist de calidad antes de publicar

- No hay palabras mal pronunciadas.
- El ritmo no suena acelerado ni robotico.
- Las pausas son naturales.
- Volumen consistente entre frases.
- No hay picos o distorsion.
