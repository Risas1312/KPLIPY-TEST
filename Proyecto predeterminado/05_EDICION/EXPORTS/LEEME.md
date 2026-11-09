# 05_EDICION · EXPORTS

Salida por defecto de `klipy.py procesar`.

## Qué contiene

- MP4 H.264, 720 × 720, 30 fps, sin audio.
- Duración máxima 10 s.
- Nombres `AAAAMMDD_slug.mp4`.
- `manifiesto.csv` con el historial de procesado.

## Siguiente paso

1. Revisa el clip completo.
2. Ejecuta:

```powershell
python 08_AUTOMATIZACION\klipy.py revisar --todo
```

3. Mueve los aprobados a `06_PUBLICAR/LISTOS`.
4. Los que fallan, a `04_SELECCION/DESCARTADOS`.

## Nota

Si usaste `--directo`, los clips van directo a `06_PUBLICAR/LISTOS` y esta carpeta queda vacía.
