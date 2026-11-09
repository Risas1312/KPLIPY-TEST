# 03_INBOX · material crudo

Aquí caen los clips tal como los descargas o grabas. **No edites aquí.**

## Flujo

1. Copia el clip.
2. Anota fuente, autor, licencia y riesgo en `01_DIARIO/IDEAS.csv` o en `07_RECURSOS/PLANTILLA_LOTE.csv`.
3. Ejecuta:

```powershell
python 08_AUTOMATIZACION\klipy.py procesar --directo
```

o doble clic en `08_AUTOMATIZACION\procesar_inbox.cmd`.

## Reglas

- Un archivo = un clip.
- Nombres claros: `gato-asustado.mp4`, `gol-celebracion.mp4`.
- Sin espacios raros ni caracteres especiales.
- Si el clip no se entiende en 3 segundos, bórralo.
- No acumules más de 2 días de material sin procesar.

## Después de procesar

Los archivos quedan en `06_PUBLICAR/LISTOS`. Corre el control de calidad y sube.
