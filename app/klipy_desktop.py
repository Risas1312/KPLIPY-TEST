#!/usr/bin/env python3
"""KLIPY Desktop: gestor local del flujo de clips. Solo usa la biblioteca estándar."""
from __future__ import annotations

import csv
import os
import shutil
import sqlite3
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

APP_TITLE = "KLIPY · Gestor de clips"
PROJECT_DEFAULT = Path(__file__).resolve().parent.parent / "Proyecto predeterminado"
STAGES = {
    "Inbox": Path("03_INBOX"),
    "Aprobados": Path("04_SELECCION/APROBADOS"),
    "Descartados": Path("04_SELECCION/DESCARTADOS"),
    "Edición": Path("05_EDICION/PROYECTOS"),
    "Exports": Path("05_EDICION/EXPORTS"),
    "Listos": Path("06_PUBLICAR/LISTOS"),
    "Subidos": Path("06_PUBLICAR/SUBIDOS"),
}
MEDIA_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv", ".gif"}
IDEA_FIELDS = ["id", "fecha", "idea", "nicho", "fuente_url", "autor", "licencia", "riesgo", "estado", "notas"]
UPLOAD_FIELDS = ["id", "fecha", "hora", "archivo", "titulo", "nicho", "tags", "url_klipy", "estado", "visitas_24h", "visitas_7d", "compartidos", "pais_top", "riesgo", "notas"]


def read_csv(path: Path, fields: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=";")
            for raw in reader:
                if not raw or not any(raw.values()):
                    continue
                row = {key: (raw.get(key) or "").strip() for key in fields}
                # Recupera notas que en el CSV de ideas existente contienen ; sin escapar.
                extras = raw.get(None) or []
                if extras and "notas" in row:
                    row["notas"] = ";".join(filter(None, [row["notas"], *extras]))
                rows.append(row)
    except (OSError, csv.Error, UnicodeError):
        return []
    return rows


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in fields} for row in rows)
    temp.replace(path)


class KlipyDesktop:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1120x720")
        self.root.minsize(850, 560)
        self.project = PROJECT_DEFAULT
        if not self.project.exists():
            self.project = Path.cwd()
        self._ensure_structure()
        self.db = sqlite3.connect(self.project / ".klipy_desktop.sqlite3")
        self.db.execute("CREATE TABLE IF NOT EXISTS clips (path TEXT PRIMARY KEY, title TEXT DEFAULT '', niche TEXT DEFAULT '', tags TEXT DEFAULT '', source TEXT DEFAULT '', author TEXT DEFAULT '', license TEXT DEFAULT '', risk TEXT DEFAULT '', notes TEXT DEFAULT '')")
        self.db.commit()
        self._style()
        self._build_ui()
        self.refresh_all()

    def _ensure_structure(self):
        for rel in STAGES.values():
            (self.project / rel).mkdir(parents=True, exist_ok=True)
        (self.project / "01_DIARIO").mkdir(parents=True, exist_ok=True)
        (self.project / "02_DESCUBRIR").mkdir(parents=True, exist_ok=True)

    def _style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=27, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", padding=(10, 6))
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("Sub.TLabel", foreground="#586174")

    def _build_ui(self):
        header = ttk.Frame(self.root, padding=(18, 14))
        header.pack(fill="x")
        ttk.Label(header, text="KLIPY", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="  ·  Producción de clips en un solo lugar", style="Sub.TLabel").pack(side="left", pady=(7, 0))
        ttk.Button(header, text="Elegir carpeta del proyecto…", command=self.choose_project).pack(side="right")
        self.path_label = ttk.Label(self.root, text=str(self.project), style="Sub.TLabel", padding=(20, 0, 20, 10))
        self.path_label.pack(fill="x")
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.home = ttk.Frame(self.tabs, padding=18)
        self.clip_tab = ttk.Frame(self.tabs, padding=14)
        self.idea_tab = ttk.Frame(self.tabs, padding=14)
        self.trend_tab = ttk.Frame(self.tabs, padding=14)
        self.upload_tab = ttk.Frame(self.tabs, padding=14)
        self.resource_tab = ttk.Frame(self.tabs, padding=18)
        for tab, label in [(self.home, "Resumen"), (self.clip_tab, "Clips"), (self.idea_tab, "Ideas"), (self.trend_tab, "Tendencias"), (self.upload_tab, "Publicados"), (self.resource_tab, "Recursos")]:
            self.tabs.add(tab, text=label)
        self._build_home()
        self._build_clips()
        self._build_ideas()
        self._build_trends()
        self._build_uploads()
        self._build_resources()

    def _build_home(self):
        ttk.Label(self.home, text="Tu flujo de producción", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.home, text="Organiza ideas, revisa clips y prepara el registro de publicación.", style="Sub.TLabel").pack(anchor="w", pady=(4, 18))
        self.metrics = ttk.Frame(self.home)
        self.metrics.pack(fill="x", pady=(0, 20))
        self.metric_labels = {}
        for name in ["Inbox", "Aprobados", "Listos", "Subidos", "Ideas"]:
            card = ttk.LabelFrame(self.metrics, text=name, padding=15)
            card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            value = ttk.Label(card, text="0", font=("Segoe UI", 24, "bold"))
            value.pack(anchor="w")
            self.metric_labels[name] = value
        ttk.Label(self.home, text="Pasos recomendados", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(8, 8))
        for text in ["1. Importa clips propios o con licencia y completa su fuente y riesgo.", "2. Revisa cada clip: aprueba, descarta o envíalo a edición.", "3. Prepara los clips finales en Listos y completa el checklist antes de subir.", "4. Registra la URL publicada para mantener actualizado el diario."]:
            ttk.Label(self.home, text=text, padding=(8, 6)).pack(anchor="w")
        ttk.Label(self.home, text="La app organiza archivos localmente; no descarga ni publica automáticamente en KLIPY.", style="Sub.TLabel").pack(anchor="w", pady=(22, 0))

    def _build_clips(self):
        bar = ttk.Frame(self.clip_tab)
        bar.pack(fill="x", pady=(0, 10))
        actions = [("Importar clips…", self.import_clips), ("Abrir", self.open_clip), ("Metadatos…", self.edit_clip), ("Aprobar", lambda: self.move_selected("Aprobados")), ("A edición", lambda: self.move_selected("Edición")), ("A Listos", lambda: self.move_selected("Listos")), ("Descartar", lambda: self.move_selected("Descartados")), ("Registrar subida…", self.register_upload)]
        for label, command in actions:
            ttk.Button(bar, text=label, command=command).pack(side="left", padx=(0, 5))
        cols = ("stage", "name", "size", "risk", "title")
        self.clip_tree = ttk.Treeview(self.clip_tab, columns=cols, show="headings", selectmode="browse")
        for col, label, width in [("stage", "Etapa", 105), ("name", "Archivo", 290), ("size", "Tamaño", 90), ("risk", "Riesgo", 90), ("title", "Título / idea", 350)]:
            self.clip_tree.heading(col, text=label)
            self.clip_tree.column(col, width=width, anchor="w")
        self.clip_tree.pack(fill="both", expand=True)
        self.clip_tree.bind("<Double-1>", lambda _e: self.edit_clip())
        ttk.Label(self.clip_tab, text="Doble clic para editar metadatos. Los movimientos se realizan dentro de la carpeta del proyecto.", style="Sub.TLabel").pack(anchor="w", pady=(8, 0))

    def _build_ideas(self):
        bar = ttk.Frame(self.idea_tab)
        bar.pack(fill="x", pady=(0, 10))
        ttk.Button(bar, text="Nueva idea", command=self.add_idea).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="Editar", command=self.edit_idea).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="Eliminar", command=self.delete_idea).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="Actualizar", command=self.refresh_ideas).pack(side="right")
        cols = ("id", "idea", "nicho", "riesgo", "estado", "fecha")
        self.idea_tree = ttk.Treeview(self.idea_tab, columns=cols, show="headings", selectmode="browse")
        for col, label, width in [("id", "ID", 90), ("idea", "Idea", 420), ("nicho", "Nicho", 110), ("riesgo", "Riesgo", 100), ("estado", "Estado", 130), ("fecha", "Fecha", 110)]:
            self.idea_tree.heading(col, text=label)
            self.idea_tree.column(col, width=width, anchor="w")
        self.idea_tree.pack(fill="both", expand=True)
        self.idea_tree.bind("<Double-1>", lambda _e: self.edit_idea())

    def _build_trends(self):
        ttk.Label(self.trend_tab, text="Términos guardados en 02_DESCUBRIR/TENDENCIAS.csv", style="Sub.TLabel").pack(anchor="w", pady=(0, 10))
        cols = ("fecha", "plataforma", "termino", "tipo", "pais", "volumen", "notas")
        self.trend_tree = ttk.Treeview(self.trend_tab, columns=cols, show="headings")
        for col, width in [("fecha", 105), ("plataforma", 180), ("termino", 140), ("tipo", 100), ("pais", 100), ("volumen", 90), ("notas", 380)]:
            self.trend_tree.heading(col, text=col.capitalize())
            self.trend_tree.column(col, width=width, anchor="w")
        self.trend_tree.pack(fill="both", expand=True)
        ttk.Button(self.trend_tab, text="Abrir archivo de tendencias", command=lambda: self.open_path(self.project / "02_DESCUBRIR/TENDENCIAS.csv")).pack(anchor="e", pady=(10, 0))

    def _build_uploads(self):
        ttk.Label(self.upload_tab, text="Historial desde 01_DIARIO/REGISTRO_SUBIDAS.csv", style="Sub.TLabel").pack(anchor="w", pady=(0, 10))
        cols = ("fecha", "archivo", "titulo", "nicho", "url_klipy", "estado", "riesgo")
        self.upload_tree = ttk.Treeview(self.upload_tab, columns=cols, show="headings")
        for col, label, width in [("fecha", "Fecha", 105), ("archivo", "Archivo", 200), ("titulo", "Título", 220), ("nicho", "Nicho", 100), ("url_klipy", "URL KLIPY", 280), ("estado", "Estado", 100), ("riesgo", "Riesgo", 90)]:
            self.upload_tree.heading(col, text=label)
            self.upload_tree.column(col, width=width, anchor="w")
        self.upload_tree.pack(fill="both", expand=True)
        ttk.Button(self.upload_tab, text="Abrir registro CSV", command=lambda: self.open_path(self.project / "01_DIARIO/REGISTRO_SUBIDAS.csv")).pack(anchor="e", pady=(10, 0))

    def _build_resources(self):
        ttk.Label(self.resource_tab, text="Documentación del flujo", style="Title.TLabel").pack(anchor="w", pady=(0, 8))
        docs = [("Checklist antes de subir", "06_PUBLICAR/CHECKLIST_ANTES_DE_SUBIR.md"), ("Banco de títulos", "07_RECURSOS/BANCO_TITULOS.md"), ("Banco de tags", "07_RECURSOS/BANCO_TAGS.md"), ("Búsquedas guardadas", "02_DESCUBRIR/BUSQUEDAS.md"), ("Fuentes y licencias", "02_DESCUBRIR/FUENTES.md"), ("Plan de hoy", "01_DIARIO/PLAN_HOY.md")]
        for label, rel in docs:
            ttk.Button(self.resource_tab, text=f"Abrir {label}", command=lambda p=self.project / rel: self.open_path(p)).pack(anchor="w", pady=5)
        ttk.Label(self.resource_tab, text="Los archivos Markdown se abren con la aplicación predeterminada del sistema.", style="Sub.TLabel").pack(anchor="w", pady=(18, 0))

    def choose_project(self):
        selected = filedialog.askdirectory(title="Selecciona la carpeta Proyecto predeterminado")
        if not selected:
            return
        self.db.close()
        self.project = Path(selected)
        self._ensure_structure()
        self.db = sqlite3.connect(self.project / ".klipy_desktop.sqlite3")
        self.db.execute("CREATE TABLE IF NOT EXISTS clips (path TEXT PRIMARY KEY, title TEXT DEFAULT '', niche TEXT DEFAULT '', tags TEXT DEFAULT '', source TEXT DEFAULT '', author TEXT DEFAULT '', license TEXT DEFAULT '', risk TEXT DEFAULT '', notes TEXT DEFAULT '')")
        self.db.commit()
        self.path_label.configure(text=str(self.project))
        self.refresh_all()

    def refresh_all(self):
        self.refresh_clips()
        self.refresh_ideas()
        self.refresh_trends()
        self.refresh_uploads()
        self.refresh_metrics()

    def refresh_metrics(self):
        for stage in ["Inbox", "Aprobados", "Listos", "Subidos"]:
            self.metric_labels[stage].configure(text=str(sum(1 for _ in self.stage_files(stage))))
        self.metric_labels["Ideas"].configure(text=str(len(read_csv(self.project / "01_DIARIO/IDEAS.csv", IDEA_FIELDS))))

    def stage_files(self, stage: str):
        folder = self.project / STAGES[stage]
        if folder.exists():
            for path in folder.rglob("*"):
                if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS:
                    yield path

    def clip_stage(self, path: Path):
        for stage, rel in STAGES.items():
            try:
                path.relative_to(self.project / rel)
                return stage
            except ValueError:
                continue
        return "Otro"

    def _metadata(self, path: Path):
        row = self.db.execute("SELECT title,niche,tags,source,author,license,risk,notes FROM clips WHERE path=?", (str(path),)).fetchone()
        if row:
            return dict(zip(["title", "niche", "tags", "source", "author", "license", "risk", "notes"], row))
        self.db.execute("INSERT OR IGNORE INTO clips(path) VALUES(?)", (str(path),))
        self.db.commit()
        return {key: "" for key in ["title", "niche", "tags", "source", "author", "license", "risk", "notes"]}

    def refresh_clips(self):
        if not hasattr(self, "clip_tree"):
            return
        self.clip_tree.delete(*self.clip_tree.get_children())
        paths = []
        for stage in STAGES:
            paths.extend(self.stage_files(stage))
        for path in sorted(set(paths), key=lambda p: (self.clip_stage(p), p.name.lower())):
            meta = self._metadata(path)
            size = f"{path.stat().st_size / (1024*1024):.1f} MB"
            self.clip_tree.insert("", "end", iid=str(path), values=(self.clip_stage(path), path.name, size, meta["risk"], meta["title"]))
        self.refresh_metrics()

    def selected_clip(self):
        selected = self.clip_tree.selection()
        return Path(selected[0]) if selected else None

    def import_clips(self):
        files = filedialog.askopenfilenames(title="Selecciona clips para importar", filetypes=[("Videos", "*.mp4 *.mov *.m4v *.webm *.avi *.mkv *.gif"), ("Todos los archivos", "*.*")])
        if not files:
            return
        inbox = self.project / STAGES["Inbox"]
        added = 0
        for filename in files:
            source = Path(filename)
            if source.suffix.lower() not in MEDIA_EXTENSIONS:
                continue
            destination = inbox / source.name
            if destination.exists():
                destination = inbox / f"{source.stem}_{datetime.now():%H%M%S}{source.suffix}"
            shutil.copy2(source, destination)
            added += 1
        self.refresh_clips()
        messagebox.showinfo("Importación", f"Se importaron {added} archivo(s) a 03_INBOX.")

    def open_clip(self):
        path = self.selected_clip()
        if path:
            self.open_path(path)
        else:
            messagebox.showwarning("Selecciona un clip", "Elige un clip de la lista primero.")

    @staticmethod
    def open_path(path: Path):
        if not path.exists():
            messagebox.showerror("No encontrado", f"No existe el archivo:\n{path}")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(path))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except (OSError, AttributeError) as exc:
            messagebox.showerror("No se pudo abrir", str(exc))

    def edit_clip(self):
        path = self.selected_clip()
        if not path:
            messagebox.showwarning("Selecciona un clip", "Elige un clip de la lista primero.")
            return
        old = self._metadata(path)
        win = tk.Toplevel(self.root)
        win.title(f"Metadatos · {path.name}")
        win.transient(self.root)
        win.grab_set()
        fields = [("title", "Título"), ("niche", "Nicho"), ("tags", "Tags (separados por coma)"), ("source", "URL de origen"), ("author", "Autor"), ("license", "Licencia / permiso"), ("risk", "Riesgo (verde / amarillo / rojo)"), ("notes", "Notas")]
        vars_ = {}
        for index, (key, label) in enumerate(fields):
            ttk.Label(win, text=label).grid(row=index, column=0, sticky="w", padx=12, pady=6)
            var = tk.StringVar(value=old[key])
            vars_[key] = var
            ttk.Entry(win, textvariable=var, width=58).grid(row=index, column=1, sticky="ew", padx=12, pady=6)
        def save():
            values = [vars_[key].get().strip() for key, _ in fields]
            self.db.execute("UPDATE clips SET title=?,niche=?,tags=?,source=?,author=?,license=?,risk=?,notes=? WHERE path=?", (*values, str(path)))
            self.db.commit()
            win.destroy()
            self.refresh_clips()
        ttk.Button(win, text="Guardar", command=save).grid(row=len(fields), column=1, sticky="e", padx=12, pady=12)
        win.columnconfigure(1, weight=1)

    def move_selected(self, stage: str):
        source = self.selected_clip()
        if not source:
            messagebox.showwarning("Selecciona un clip", "Elige un clip de la lista primero.")
            return
        if stage == "Listos":
            meta = self._metadata(source)
            if meta["risk"].strip().lower() == "rojo":
                messagebox.showerror("Riesgo rojo", "No se permite pasar un clip marcado con riesgo rojo a Listos.")
                return
            if not meta["source"] or not meta["license"]:
                if not messagebox.askyesno("Faltan datos de derechos", "No has registrado fuente o licencia. ¿Quieres continuar de todos modos?"):
                    return
        destination_dir = self.project / STAGES[stage]
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / source.name
        if destination.exists():
            destination = destination_dir / f"{source.stem}_{datetime.now():%Y%m%d_%H%M%S}{source.suffix}"
        old_meta = self._metadata(source)
        try:
            shutil.move(str(source), str(destination))
        except OSError as exc:
            messagebox.showerror("No se pudo mover", str(exc))
            return
        self.db.execute("DELETE FROM clips WHERE path=?", (str(source),))
        self.db.execute("INSERT OR REPLACE INTO clips(path,title,niche,tags,source,author,license,risk,notes) VALUES(?,?,?,?,?,?,?,?,?)", (str(destination), *[old_meta[k] for k in ["title", "niche", "tags", "source", "author", "license", "risk", "notes"]]))
        self.db.commit()
        self.refresh_clips()

    def refresh_ideas(self):
        if not hasattr(self, "idea_tree"):
            return
        self.idea_tree.delete(*self.idea_tree.get_children())
        self.ideas = read_csv(self.project / "01_DIARIO/IDEAS.csv", IDEA_FIELDS)
        for i, row in enumerate(self.ideas):
            self.idea_tree.insert("", "end", iid=str(i), values=(row["id"], row["idea"], row["nicho"], row["riesgo"], row["estado"], row["fecha"]))
        self.refresh_metrics()

    def idea_dialog(self, data=None):
        data = data or {key: "" for key in IDEA_FIELDS}
        win = tk.Toplevel(self.root)
        win.title("Idea" if not data.get("id") else "Editar idea")
        win.transient(self.root)
        win.grab_set()
        fields = [("idea", "Idea"), ("nicho", "Nicho"), ("fuente_url", "URL fuente"), ("autor", "Autor"), ("licencia", "Licencia"), ("riesgo", "Riesgo"), ("estado", "Estado"), ("notas", "Notas")]
        vars_ = {}
        if data.get("id"):
            ttk.Label(win, text=f"ID: {data['id']}").grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=6)
        for index, (key, label) in enumerate(fields, start=1):
            ttk.Label(win, text=label).grid(row=index, column=0, sticky="w", padx=12, pady=5)
            var = tk.StringVar(value=data.get(key, ""))
            vars_[key] = var
            ttk.Entry(win, textvariable=var, width=58).grid(row=index, column=1, sticky="ew", padx=12, pady=5)
        def save():
            if not vars_["idea"].get().strip():
                messagebox.showwarning("Falta la idea", "Escribe una descripción para la idea.", parent=win)
                return
            record = {key: vars_[key].get().strip() for key, _ in fields}
            record["id"] = data.get("id") or self.next_idea_id()
            record["fecha"] = data.get("fecha") or datetime.now().strftime("%Y-%m-%d")
            if data.get("id"):
                self.ideas[int(self.idea_tree.selection()[0])] = record
            else:
                self.ideas.append(record)
            write_csv(self.project / "01_DIARIO/IDEAS.csv", IDEA_FIELDS, self.ideas)
            win.destroy()
            self.refresh_ideas()
        ttk.Button(win, text="Guardar", command=save).grid(row=len(fields)+1, column=1, sticky="e", padx=12, pady=12)
        win.columnconfigure(1, weight=1)

    def next_idea_id(self):
        nums = []
        for row in self.ideas:
            try:
                nums.append(int(row["id"].split("-")[-1]))
            except (ValueError, IndexError):
                pass
        return f"IDEA-{max(nums, default=0)+1:03d}"

    def add_idea(self):
        self.idea_dialog()

    def edit_idea(self):
        selected = self.idea_tree.selection()
        if selected:
            self.idea_dialog(self.ideas[int(selected[0])])
        else:
            messagebox.showwarning("Selecciona una idea", "Elige una idea primero.")

    def delete_idea(self):
        selected = self.idea_tree.selection()
        if not selected:
            messagebox.showwarning("Selecciona una idea", "Elige una idea primero.")
            return
        index = int(selected[0])
        if messagebox.askyesno("Eliminar idea", f"¿Eliminar {self.ideas[index]['id']}? Esta acción no se puede deshacer."):
            del self.ideas[index]
            write_csv(self.project / "01_DIARIO/IDEAS.csv", IDEA_FIELDS, self.ideas)
            self.refresh_ideas()

    def refresh_trends(self):
        self.trend_tree.delete(*self.trend_tree.get_children())
        fields = ["fecha", "plataforma", "termino", "tipo", "pais", "volumen", "notas"]
        rows = read_csv(self.project / "02_DESCUBRIR/TENDENCIAS.csv", fields)
        for index, row in enumerate(rows):
            self.trend_tree.insert("", "end", iid=str(index), values=tuple(row[f] for f in fields))

    def refresh_uploads(self):
        self.upload_tree.delete(*self.upload_tree.get_children())
        for index, row in enumerate(read_csv(self.project / "01_DIARIO/REGISTRO_SUBIDAS.csv", UPLOAD_FIELDS)):
            self.upload_tree.insert("", "end", iid=str(index), values=tuple(row[key] for key in ["fecha", "archivo", "titulo", "nicho", "url_klipy", "estado", "riesgo"]))

    def register_upload(self):
        path = self.selected_clip()
        if not path:
            messagebox.showwarning("Selecciona un clip", "Elige el archivo final que acabas de subir.")
            return
        if self.clip_stage(path) != "Listos":
            if not messagebox.askyesno("El clip no está en Listos", "El clip debería pasar el checklist y estar en Listos. ¿Quieres registrar la subida de todos modos?"):
                return
        meta = self._metadata(path)
        url = simpledialog.askstring("Registro de subida", "Pega la URL publicada en KLIPY:", parent=self.root)
        if url is None:
            return
        if not url.strip():
            messagebox.showwarning("Falta la URL", "Introduce la URL del clip publicado.")
            return
        now = datetime.now()
        rows = read_csv(self.project / "01_DIARIO/REGISTRO_SUBIDAS.csv", UPLOAD_FIELDS)
        rows.append({"id": f"UPLOAD-{now:%Y%m%d%H%M%S}", "fecha": now.strftime("%Y-%m-%d"), "hora": now.strftime("%H:%M"), "archivo": path.name, "titulo": meta["title"], "nicho": meta["niche"], "tags": meta["tags"], "url_klipy": url.strip(), "estado": "pendiente", "visitas_24h": "", "visitas_7d": "", "compartidos": "", "pais_top": "", "riesgo": meta["risk"], "notas": meta["notes"]})
        write_csv(self.project / "01_DIARIO/REGISTRO_SUBIDAS.csv", UPLOAD_FIELDS, rows)
        destination = self.project / STAGES["Subidos"] / f"{now:%Y%m%d}_{path.name}"
        if destination.exists():
            destination = destination.with_name(f"{now:%H%M%S}_{destination.name}")
        old_meta = meta
        try:
            shutil.move(str(path), str(destination))
            self.db.execute("DELETE FROM clips WHERE path=?", (str(path),))
            self.db.execute("INSERT OR REPLACE INTO clips(path,title,niche,tags,source,author,license,risk,notes) VALUES(?,?,?,?,?,?,?,?,?)", (str(destination), *[old_meta[k] for k in ["title", "niche", "tags", "source", "author", "license", "risk", "notes"]]))
            self.db.commit()
        except OSError as exc:
            messagebox.showerror("Registro guardado, movimiento fallido", f"La subida se registró, pero el archivo no se pudo mover:\n{exc}")
        self.refresh_all()
        self.tabs.select(self.upload_tab)
        messagebox.showinfo("Subida registrada", "Se actualizó el CSV y el archivo se archivó en 06_PUBLICAR/SUBIDOS.")


def main():
    root = tk.Tk()
    KlipyDesktop(root)
    root.mainloop()


if __name__ == "__main__":
    main()
