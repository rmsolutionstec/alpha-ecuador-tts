# Modelo gratuito y comunitario

## Compromiso

Studio TTS Latino es gratuito, abierto y utilizable sin una cuenta. Las funciones no
se bloquean detras de pagos, publicidad o limites artificiales en la version de escritorio.

## Financiamiento voluntario

El proyecto puede sostenerse mediante:

- GitHub Sponsors.
- Un enlace real de PayPal u otro medio permitido en Ecuador.
- Patrocinios voluntarios de empresas que utilicen el proyecto.
- Colaboraciones, correcciones y documentacion aportadas por la comunidad.

## Configurar GitHub Sponsors

1. Crea y verifica el perfil de patrocinador en GitHub.
2. Revisa la informacion bancaria, fiscal y de identidad solicitada por GitHub.
3. Edita `.github/FUNDING.yml` con el usuario real del mantenedor.
4. Explica claramente que las contribuciones son voluntarias.

Ejemplo:

```yaml
github: [usuario-real]
custom: ["https://enlace-real-de-apoyo"]
```

No actives enlaces ficticios, cuentas incorrectas ni informacion de pago en el repositorio.

## Configurar la aplicacion

```powershell
$env:STUDIO_TTS_DONATION_URL = "https://enlace-real-de-apoyo"
python gui.py
```

Si la variable no existe, el boton abre `https://alphaecuador.com`.

## Buenas practicas

- Mantener el patrocinio opcional.
- No limitar funciones por falta de donaciones.
- Agradecer a patrocinadores solo si aceptan aparecer publicamente.
- Publicar una hoja de ruta transparente.
- No asumir que una contribucion voluntaria elimina obligaciones fiscales.
