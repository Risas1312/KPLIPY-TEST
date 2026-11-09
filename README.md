# KLIPY Desktop

Aplicación de escritorio local para organizar el flujo de producción de clips del repositorio. Reúne importación de videos, revisión y clasificación, metadatos de derechos, ideas, tendencias y registro de publicaciones. Está hecha con Python y Tkinter; no requiere paquetes externos.

## Requisitos

- Python 3.10 o posterior.
- Tkinter, incluido normalmente con Python. En algunas distribuciones Linux se instala aparte (por ejemplo, `python3-tk`).

## Iniciar

Desde la carpeta raíz del repositorio:

```bash
python app/klipy_desktop.py
```

La aplicación abre por defecto `Proyecto predeterminado/`. Si trabajas con una copia en otra ubicación, usa **Elegir carpeta del proyecto…** y selecciona esa carpeta. El programa crea las carpetas de flujo que falten.

## Funciones

- **Resumen:** conteo de clips por etapa e ideas guardadas.
- **Clips:** importa videos a `03_INBOX`, abre el archivo en el reproductor del sistema, guarda título/nicho/tags/fuente/autor/licencia/riesgo/notas y mueve clips entre Inbox, Aprobados, Edición, Listos, Descartados y Subidos.
- **Ideas:** crea, edita y elimina ideas, manteniendo `01_DIARIO/IDEAS.csv`.
- **Tendencias:** consulta `02_DESCUBRIR/TENDENCIAS.csv`.
- **Publicados:** registra URL, metadata y fecha en `01_DIARIO/REGISTRO_SUBIDAS.csv`; después archiva el video en `06_PUBLICAR/SUBIDOS`.
- **Recursos:** abre las guías Markdown existentes con la aplicación predeterminada del sistema.

La información de metadatos de clips se guarda localmente en `.klipy_desktop.sqlite3` dentro de la carpeta del proyecto. Los videos se copian al importar y se mueven entre etapas; no se transcodifican ni se suben automáticamente. Antes de publicar, revisa siempre los derechos y `06_PUBLICAR/CHECKLIST_ANTES_DE_SUBIR.md`. Los clips con riesgo marcado como `rojo` no se pueden mover a Listos.

## Crear un ejecutable

Puedes empaquetar la app opcionalmente con PyInstaller (no es requisito para ejecutarla):

```bash
python -m pip install pyinstaller
pyinstaller --onefile --windowed app/klipy_desktop.py --name KlipyDesktop
```

El ejecutable quedará en `dist/`.
