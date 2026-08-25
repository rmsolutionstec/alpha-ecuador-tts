"""Interfaz profesional para texto a voz con enfoque en locucion latina."""
from __future__ import annotations

import os
import logging
import threading
import tempfile
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlparse

from . import APP_NAME, COMPANY_NAME, DEVELOPER_NAME, PROJECT_WEBSITE, __version__
from .core import (
    DEFAULT_PROFILE,
    DEFAULT_PRONUNCIATION_FILE,
    DEFAULT_MASTERING_PRESET,
    DELIVERY_MODES,
    EDGE_DEFAULT_VOICE,
    EDGE_STYLES,
    EDGE_VOICE_OPTIONS,
    EMOTION_PRESETS,
    MASTERING_PRESETS,
    VOICE_PROFILES,
    has_ffmpeg,
    normalize_output_path,
    synthesize,
)
from .settings import configure_logging, load_preferences, save_preferences


LOGGER = logging.getLogger(__name__)


def safe_read(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception as exc:
        messagebox.showerror("Error", f"No se pudo leer el archivo:\n{exc}")
        return ""


class TTSApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(f"{APP_NAME} {__version__}")
        self.root.geometry("980x680")
        self.root.minsize(860, 600)

        self.output_var = tk.StringVar(value=str(Path.cwd() / "salida_gui.mp3"))
        self.rate_var = tk.IntVar(value=176)
        self.volume_var = tk.DoubleVar(value=100.0)
        self.voice_hint_var = tk.StringVar(value=EDGE_DEFAULT_VOICE)
        self.male_var = tk.BooleanVar(value=True)
        self.provider_var = tk.StringVar(value="edge")
        self.profile_var = tk.StringVar(value=DEFAULT_PROFILE)
        self.style_var = tk.StringVar(value="narration-professional")
        self.pause_var = tk.IntVar(value=250)
        self.natural_mode_var = tk.BooleanVar(value=True)
        self.delivery_mode_var = tk.StringVar(value="podcast")
        self.emotion_var = tk.StringVar(value="neutro")
        self.pronunciation_file_var = tk.StringVar(value=DEFAULT_PRONUNCIATION_FILE)
        self.mastering_preset_var = tk.StringVar(value=DEFAULT_MASTERING_PRESET)
        self.rate_display_var = tk.StringVar(value="176")
        self.volume_display_var = tk.StringVar(value="100")
        self.pause_display_var = tk.StringVar(value="250")

        self._build_style()
        self._build_layout()
        self.apply_profile(DEFAULT_PROFILE)
        self._restore_preferences()
        self.root.protocol("WM_DELETE_WINDOW", self._close_application)

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _build_style(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 11))
        style.configure("Primary.TButton", padding=(10, 6))

    def _build_layout(self) -> None:
        root_pad = ttk.Frame(self.root, padding=12)
        root_pad.pack(fill="both", expand=True)

        top = ttk.Frame(root_pad)
        top.pack(fill="both", expand=True)
        top.columnconfigure(0, weight=2)
        top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)

        text_panel = ttk.LabelFrame(top, text="Paso 1: Texto")
        text_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.text_widget = tk.Text(text_panel, wrap="word", height=20, font=("Segoe UI", 11))
        text_scroll = ttk.Scrollbar(text_panel, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=text_scroll.set)
        self.text_widget.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        text_scroll.pack(side="right", fill="y", padx=(0, 8), pady=8)

        right_panel = ttk.LabelFrame(top, text="Paso 2: Voz y Estilo")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.columnconfigure(1, weight=1)

        ttk.Label(right_panel, text="Perfil", style="Title.TLabel").grid(row=0, column=0, sticky="w", padx=8, pady=(10, 4))
        self.profile_combo = ttk.Combobox(
            right_panel,
            textvariable=self.profile_var,
            values=sorted(VOICE_PROFILES),
            state="readonly",
        )
        self.profile_combo.grid(row=0, column=1, sticky="ew", padx=8, pady=(10, 4))
        self.profile_combo.bind("<<ComboboxSelected>>", lambda _e: self.apply_profile(self.profile_var.get()))

        ttk.Label(right_panel, text="Proveedor").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.provider_combo = ttk.Combobox(
            right_panel,
            textvariable=self.provider_var,
            values=["edge", "local"],
            state="readonly",
        )
        self.provider_combo.grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        ttk.Label(right_panel, text="Voz latina").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.voice_combo = ttk.Combobox(
            right_panel,
            textvariable=self.voice_hint_var,
            values=EDGE_VOICE_OPTIONS,
            state="normal",
        )
        self.voice_combo.grid(row=2, column=1, sticky="ew", padx=8, pady=4)

        ttk.Label(right_panel, text="Estilo de locucion").grid(row=3, column=0, sticky="w", padx=8, pady=4)
        ttk.Combobox(
            right_panel,
            textvariable=self.style_var,
            values=EDGE_STYLES,
            state="readonly",
        ).grid(row=3, column=1, sticky="ew", padx=8, pady=4)

        ttk.Label(right_panel, text="Velocidad (wpm)").grid(row=4, column=0, sticky="w", padx=8, pady=4)
        ttk.Scale(
            right_panel,
            from_=130,
            to=230,
            orient="horizontal",
            variable=self.rate_var,
            command=self._on_rate_change,
        ).grid(
            row=4, column=1, sticky="ew", padx=8, pady=4
        )
        ttk.Label(right_panel, textvariable=self.rate_display_var, width=4).grid(row=4, column=2, sticky="e", padx=(0, 8))

        ttk.Label(right_panel, text="Volumen (0-100)").grid(row=5, column=0, sticky="w", padx=8, pady=4)
        ttk.Scale(
            right_panel,
            from_=50,
            to=100,
            orient="horizontal",
            variable=self.volume_var,
            command=self._on_volume_change,
        ).grid(
            row=5, column=1, sticky="ew", padx=8, pady=4
        )
        ttk.Label(right_panel, textvariable=self.volume_display_var, width=4).grid(row=5, column=2, sticky="e", padx=(0, 8))

        ttk.Label(right_panel, text="Pausa entre lineas (ms aprox.)").grid(row=6, column=0, sticky="w", padx=8, pady=4)
        ttk.Scale(
            right_panel,
            from_=0,
            to=900,
            orient="horizontal",
            variable=self.pause_var,
            command=self._on_pause_change,
        ).grid(
            row=6, column=1, sticky="ew", padx=8, pady=4
        )
        ttk.Label(right_panel, textvariable=self.pause_display_var, width=4).grid(row=6, column=2, sticky="e", padx=(0, 8))

        ttk.Checkbutton(right_panel, text="Preferir voz masculina", variable=self.male_var).grid(
            row=7, column=1, sticky="w", padx=8, pady=(4, 10)
        )

        ttk.Checkbutton(
            right_panel,
            text="Modo locutor natural (recomendado)",
            variable=self.natural_mode_var,
        ).grid(row=8, column=1, sticky="w", padx=8, pady=(0, 12))

        ttk.Label(right_panel, text="Modo de entrega").grid(row=9, column=0, sticky="w", padx=8, pady=4)
        ttk.Combobox(
            right_panel,
            textvariable=self.delivery_mode_var,
            values=sorted(DELIVERY_MODES),
            state="readonly",
        ).grid(row=9, column=1, sticky="ew", padx=8, pady=4)

        ttk.Label(right_panel, text="Emocion").grid(row=10, column=0, sticky="w", padx=8, pady=4)
        ttk.Combobox(
            right_panel,
            textvariable=self.emotion_var,
            values=sorted(EMOTION_PRESETS),
            state="readonly",
        ).grid(row=10, column=1, sticky="ew", padx=8, pady=4)

        ttk.Label(right_panel, text="Mastering").grid(row=11, column=0, sticky="w", padx=8, pady=4)
        ttk.Combobox(
            right_panel,
            textvariable=self.mastering_preset_var,
            values=sorted(MASTERING_PRESETS),
            state="readonly",
        ).grid(row=11, column=1, sticky="ew", padx=8, pady=4)

        bottom = ttk.LabelFrame(root_pad, text="Paso 3: Exportacion")
        bottom.pack(fill="x", pady=(10, 0))
        bottom.columnconfigure(1, weight=1)

        ttk.Button(bottom, text="Abrir archivo", command=self.load_file).grid(row=0, column=0, padx=8, pady=8, sticky="w")
        ttk.Button(bottom, text="Guardar como", command=self.choose_output).grid(row=0, column=1, padx=8, pady=8, sticky="w")

        ttk.Label(bottom, text="Salida MP3").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(bottom, textvariable=self.output_var).grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        ttk.Label(bottom, text="Diccionario pronunciacion").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        pronunciation_row = ttk.Frame(bottom)
        pronunciation_row.grid(row=2, column=1, sticky="ew", padx=8, pady=4)
        pronunciation_row.columnconfigure(0, weight=1)
        ttk.Entry(pronunciation_row, textvariable=self.pronunciation_file_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(pronunciation_row, text="Elegir", command=self.choose_pronunciation_file).grid(row=0, column=1, padx=(6, 0))

        action_row = ttk.Frame(bottom)
        action_row.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=8)
        action_row.columnconfigure(4, weight=1)

        self.preview_quick_btn = ttk.Button(
            action_row,
            text="Preescucha rapida",
            style="Primary.TButton",
            command=self.preview_quick_tts,
        )
        self.preview_quick_btn.grid(row=0, column=0, padx=(0, 6))
        self.preview_final_btn = ttk.Button(
            action_row,
            text="Preescucha final",
            style="Primary.TButton",
            command=self.preview_final_tts,
        )
        self.preview_final_btn.grid(row=0, column=1, padx=(0, 6))
        self.convert_btn = ttk.Button(action_row, text="Exportar MP3", style="Primary.TButton", command=self.run_tts)
        self.convert_btn.grid(row=0, column=2, padx=(0, 8))

        self.progress = ttk.Progressbar(action_row, mode="indeterminate", length=220)
        self.progress.grid(row=0, column=3, padx=(0, 10))

        self.status_var = tk.StringVar(value="Listo para generar voz latina tipo locutor")
        ttk.Label(action_row, textvariable=self.status_var).grid(row=0, column=4, sticky="w")

        footer = ttk.Frame(root_pad)
        footer.pack(fill="x", pady=(8, 0))
        ttk.Label(
            footer,
            text=f"{COMPANY_NAME} · Desarrollado por {DEVELOPER_NAME} · Proyecto gratuito",
        ).pack(side="left")
        ttk.Button(
            footer,
            text="Apoyar el proyecto",
            command=self.open_support_page,
        ).pack(side="right")

    def _restore_preferences(self) -> None:
        preferences = load_preferences()
        profile = preferences.get("profile")
        if isinstance(profile, str) and profile in VOICE_PROFILES:
            self.profile_var.set(profile)
            self.apply_profile(profile)

        variables = {
            "output": self.output_var,
            "rate": self.rate_var,
            "volume": self.volume_var,
            "voice_hint": self.voice_hint_var,
            "prefer_male": self.male_var,
            "provider": self.provider_var,
            "style": self.style_var,
            "pause_ms": self.pause_var,
            "natural_mode": self.natural_mode_var,
            "delivery_mode": self.delivery_mode_var,
            "emotion": self.emotion_var,
            "pronunciation_file": self.pronunciation_file_var,
            "mastering_preset": self.mastering_preset_var,
        }
        for name, variable in variables.items():
            if name not in preferences:
                continue
            try:
                variable.set(preferences[name])
            except (tk.TclError, TypeError, ValueError):
                LOGGER.warning("Se ignoro una preferencia invalida: %s", name)
        self._refresh_slider_labels()

    def _save_preferences(self) -> None:
        preferences = {
            "output": self.output_var.get(),
            "profile": self.profile_var.get(),
            "rate": int(self.rate_var.get()),
            "volume": float(self.volume_var.get()),
            "voice_hint": self.voice_hint_var.get(),
            "prefer_male": bool(self.male_var.get()),
            "provider": self.provider_var.get(),
            "style": self.style_var.get(),
            "pause_ms": int(self.pause_var.get()),
            "natural_mode": bool(self.natural_mode_var.get()),
            "delivery_mode": self.delivery_mode_var.get(),
            "emotion": self.emotion_var.get(),
            "pronunciation_file": self.pronunciation_file_var.get(),
            "mastering_preset": self.mastering_preset_var.get(),
        }
        try:
            save_preferences(preferences)
        except OSError as exc:
            LOGGER.warning("No se pudieron guardar las preferencias: %s", exc)

    def _close_application(self) -> None:
        self._save_preferences()
        self.root.destroy()

    def open_support_page(self) -> None:
        support_url = os.getenv("STUDIO_TTS_DONATION_URL", PROJECT_WEBSITE)
        parsed_url = urlparse(support_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            LOGGER.warning("Se rechazo un enlace de apoyo invalido")
            messagebox.showwarning(
                "Enlace no valido",
                "El enlace de apoyo debe ser una direccion web HTTP o HTTPS.",
            )
            return
        webbrowser.open(support_url)

    def load_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if not path:
            return
        content = safe_read(path)
        if content:
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, content)

    def choose_output(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("Audio MP3", "*.mp3"), ("Todos", "*.*")],
        )
        if path:
            self.output_var.set(str(Path(path).with_suffix(".mp3")))

    def choose_pronunciation_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("Todos", "*.*")])
        if path:
            self.pronunciation_file_var.set(path)

    def apply_profile(self, name: str) -> None:
        profile = VOICE_PROFILES.get(name)
        if not profile:
            return
        self.rate_var.set(int(profile.get("rate", self.rate_var.get())))
        self.volume_var.set(float(profile.get("volume", 1.0)) * 100.0)
        self.voice_hint_var.set(str(profile.get("voice_hint", EDGE_DEFAULT_VOICE)))
        self.male_var.set(bool(profile.get("prefer_male", self.male_var.get())))
        self.style_var.set(str(profile.get("style", self.style_var.get())))
        self.pause_var.set(int(profile.get("pause_ms", self.pause_var.get())))
        self._refresh_slider_labels()
        self.set_status(f"Perfil aplicado: {name}")

    def _on_rate_change(self, value: str) -> None:
        self.rate_display_var.set(str(int(float(value))))

    def _on_volume_change(self, value: str) -> None:
        self.volume_display_var.set(str(int(float(value))))

    def _on_pause_change(self, value: str) -> None:
        self.pause_display_var.set(str(int(float(value))))

    def _refresh_slider_labels(self) -> None:
        self.rate_display_var.set(str(int(self.rate_var.get())))
        self.volume_display_var.set(str(int(float(self.volume_var.get()))))
        self.pause_display_var.set(str(int(self.pause_var.get())))

    def _collect_request(self) -> tuple[str, Path, dict]:
        text = self.text_widget.get("1.0", tk.END).strip()
        if not text:
            raise ValueError("Escriba o cargue texto para convertir.")

        output_path = Path(self.output_var.get()).expanduser()
        output_path, audio_format = normalize_output_path(
            self.provider_var.get(),
            output_path,
            "mp3",
        )
        self.output_var.set(str(output_path))

        params = {
            "rate": int(self.rate_var.get()),
            "volume": max(0.0, min(1.0, float(self.volume_var.get()) / 100.0)),
            "voice_hint": self.voice_hint_var.get().strip() or None,
            "prefer_male": bool(self.male_var.get()),
            "provider": self.provider_var.get(),
            "audio_format": audio_format,
            "style": self.style_var.get().strip() or None,
            "pause_ms": int(self.pause_var.get()),
            "profile": self.profile_var.get(),
            "natural_mode": bool(self.natural_mode_var.get()),
            "delivery_mode": self.delivery_mode_var.get(),
            "emotion": self.emotion_var.get(),
            "pronunciation_file": self.pronunciation_file_var.get().strip() or None,
            "mastering_preset": self.mastering_preset_var.get(),
        }
        return text, output_path, params

    def _set_busy(self, busy: bool) -> None:
        if busy:
            self.convert_btn.state(["disabled"])
            self.preview_quick_btn.state(["disabled"])
            self.preview_final_btn.state(["disabled"])
            self.progress.start(10)
            return
        self.progress.stop()
        self.convert_btn.state(["!disabled"])
        self.preview_quick_btn.state(["!disabled"])
        self.preview_final_btn.state(["!disabled"])

    def preview_quick_tts(self) -> None:
        self._preview_tts(final_quality=False)

    def preview_final_tts(self) -> None:
        self._preview_tts(final_quality=True)

    def _preview_tts(self, final_quality: bool) -> None:
        try:
            text, _, params = self._collect_request()
        except Exception as exc:
            messagebox.showwarning("Sin texto", str(exc))
            return

        if not final_quality:
            text = " ".join(text.split())[:260]
            if not text:
                messagebox.showwarning("Sin texto", "No hay texto suficiente para preescucha.")
                return

        preview_path = Path(tempfile.gettempdir()) / "studio_tts_latino_preview.mp3"
        self._set_busy(True)
        self.set_status(
            "Generando preescucha final..." if final_quality else "Generando preescucha rapida..."
        )

        def worker() -> None:
            try:
                synthesize(text, preview_path, enable_mastering=final_quality, **params)
                self.root.after(0, lambda: self.set_status(f"Preescucha lista: {preview_path.name}"))
                try:
                    os.startfile(str(preview_path))
                except Exception:
                    pass
            except Exception as exc:
                error_message = f"No se pudo generar la preescucha:\n{exc}"
                LOGGER.exception("Error durante la preescucha")
                self.root.after(0, lambda message=error_message: messagebox.showerror("Error", message))
                self.root.after(0, lambda: self.set_status("Error en preescucha"))
            finally:
                self.root.after(0, lambda: self._set_busy(False))

        threading.Thread(target=worker, daemon=True).start()

    def run_tts(self) -> None:
        try:
            text, output_path, params = self._collect_request()
        except Exception as exc:
            messagebox.showwarning("Sin texto", str(exc))
            return

        if params["provider"] == "local" and not has_ffmpeg():
            messagebox.showwarning(
                "FFmpeg requerido",
                "Para usar el proveedor local con salida MP3, instala FFmpeg o cambia a proveedor edge.",
            )
            return

        self._set_busy(True)
        self.set_status("Generando audio profesional...")

        def worker() -> None:
            try:
                synthesize(text, output_path, enable_mastering=True, **params)
                status_msg = f"Exportado MP3: {output_path.name}"
                if not has_ffmpeg():
                    status_msg += " (sin mastering: FFmpeg no instalado)"
                self.root.after(0, lambda: self.set_status(status_msg))
            except Exception as exc:
                error_message = f"No se pudo generar el audio:\n{exc}"
                LOGGER.exception("Error durante la exportacion")
                self.root.after(0, lambda message=error_message: messagebox.showerror("Error", message))
                self.root.after(0, lambda: self.set_status("Error"))
            finally:
                self.root.after(0, lambda: self._set_busy(False))

        threading.Thread(target=worker, daemon=True).start()


def main() -> None:
    configure_logging()
    root = tk.Tk()
    TTSApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
