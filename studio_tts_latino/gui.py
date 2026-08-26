"""Interfaz Qt moderna para Alpha Studio TTS Latino."""
from __future__ import annotations

import logging
import os
import sys
import tempfile
import threading
import webbrowser
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from PySide6.QtCore import Qt, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QFileDialog, QFormLayout, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow,
    QMessageBox, QProgressBar, QPushButton, QScrollArea, QSlider, QSplitter,
    QTextEdit, QToolButton, QVBoxLayout, QWidget,
)

from . import APP_NAME, COMPANY_NAME, DEVELOPER_NAME, PROJECT_WEBSITE, __version__
from .core import (
    DEFAULT_MASTERING_PRESET, DEFAULT_PROFILE, DEFAULT_PRONUNCIATION_FILE,
    DELIVERY_MODES, EDGE_DEFAULT_VOICE, EDGE_STYLES, EDGE_VOICE_OPTIONS,
    EMOTION_PRESETS, MASTERING_PRESETS, VOICE_PROFILES, has_ffmpeg,
    normalize_output_path, synthesize,
)
from .settings import (
    append_render_history, configure_logging, load_preferences, load_render_history,
    save_preferences,
)
from .subtitles import write_srt


LOGGER = logging.getLogger(__name__)

APP_STYLESHEET = """
QMainWindow, QWidget#central { background: #F4F7FB; color: #172B4D; }
QLabel { color: #172B4D; }
QFrame#header { background: #102A43; border-radius: 14px; }
QFrame#card { background: #FFFFFF; border: 1px solid #DCE5F0; border-radius: 12px; }
QLabel#appTitle { color: #FFFFFF; font: 700 22px "Segoe UI"; }
QLabel#appSubtitle { color: #C9D8E8; font: 10pt "Segoe UI"; }
QLabel#stepLabel { color: #2475D0; font: 700 9pt "Segoe UI"; }
QLabel#sectionTitle { color: #102A43; font: 700 15px "Segoe UI"; }
QLabel#muted { color: #6B7C93; font: 9pt "Segoe UI"; }
QLabel#valueLabel { color: #2475D0; font: 700 9pt "Segoe UI"; min-width: 42px; }
QLabel#statusPill { background: #E6F4EA; color: #137333; border-radius: 10px; padding: 5px 10px; font: 700 9pt "Segoe UI"; }
QLineEdit, QComboBox, QTextEdit { background: #FFFFFF; color: #172B4D; border: 1px solid #C8D5E3; border-radius: 7px; padding: 7px 9px; font: 10pt "Segoe UI"; }
QTextEdit { padding: 12px; }
QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border: 2px solid #3A86E9; }
QComboBox::drop-down { border: 0; width: 28px; }
QPushButton { background: #FFFFFF; color: #172B4D; border: 1px solid #C8D5E3; border-radius: 7px; padding: 8px 12px; font: 600 10pt "Segoe UI"; }
QPushButton:hover { background: #EDF4FC; border-color: #82AEE0; }
QPushButton:disabled { color: #97A6B5; background: #F2F5F8; border-color: #E1E8EF; }
QPushButton#primaryButton { background: #2475D0; color: #FFFFFF; border: 1px solid #2475D0; padding: 10px 18px; font: 700 10pt "Segoe UI"; }
QPushButton#primaryButton:hover { background: #145DAA; }
QPushButton#linkButton { border: 0; color: #2475D0; padding: 4px; text-align: left; }
QToolButton { background: #FFFFFF; color: #243B53; border: 1px solid #C8D5E3; border-radius: 6px; padding: 6px 9px; font: 600 9pt "Segoe UI"; }
QToolButton:hover { background: #EDF4FC; border-color: #82AEE0; }
QGroupBox { background: #FFFFFF; border: 1px solid #DCE5F0; border-radius: 8px; color: #243B53; font: 600 10pt "Segoe UI"; margin-top: 14px; padding: 10px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QSlider::groove:horizontal { height: 6px; background: #DCE5F0; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #4A90E2; border-radius: 3px; }
QSlider::handle:horizontal { background: #2475D0; width: 16px; margin: -5px 0; border-radius: 8px; }
QProgressBar { border: 0; background: #E7EDF4; border-radius: 4px; max-height: 7px; }
QProgressBar::chunk { background: #2475D0; border-radius: 4px; }
QWidget#advancedPanel { background: #FFFFFF; }
QScrollBar:vertical { background: #F0F4F8; width: 10px; margin: 2px; border-radius: 5px; }
QScrollBar::handle:vertical { background: #AFC2D6; min-height: 28px; border-radius: 5px; }
QScrollBar::handle:vertical:hover { background: #7E9FBE; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


def safe_read(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        LOGGER.warning("No se pudo leer el archivo %s: %s", path, exc)
        QMessageBox.critical(None, "Error", f"No se pudo leer el archivo:\n{exc}")
        return ""


def create_preview_path(final_quality: bool) -> Path:
    """Devuelve una ruta única fuera del proyecto para cada preescucha."""
    quality = "final" if final_quality else "rapida"
    return Path(tempfile.gettempdir()) / "alpha_studio_tts_latino" / f"preescucha-{quality}-{uuid4().hex}.mp3"


def is_safe_support_url(url: str) -> bool:
    """Acepta únicamente enlaces web completos para abrir desde la aplicación."""
    parsed_url = urlparse(url)
    return parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)


class TTSApp(QMainWindow):
    """Ventana principal; el motor TTS permanece separado de la interfaz."""

    status_requested = Signal(str)
    error_requested = Signal(str, str)
    preview_ready = Signal(str)
    task_finished = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._active_jobs = 0
        self._export_active = False
        self.setWindowTitle(f"{APP_NAME} {__version__}")
        self.resize(1180, 780)
        self.setMinimumSize(980, 680)
        self._build_layout()
        self._connect_signals()
        self.apply_profile(DEFAULT_PROFILE)
        self._restore_preferences()

    def _connect_signals(self) -> None:
        self.status_requested.connect(self.set_status)
        self.error_requested.connect(self._show_error)
        self.preview_ready.connect(self._open_preview)
        self.task_finished.connect(self._finish_task)

    @staticmethod
    def _card() -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        return card, layout

    @staticmethod
    def _heading(step: str, title: str, description: str) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(2)
        for text, name in ((step, "stepLabel"), (title, "sectionTitle"), (description, "muted")):
            label = QLabel(text)
            label.setObjectName(name)
            label.setWordWrap(name == "muted")
            layout.addWidget(label)
        return layout

    @staticmethod
    def _combo(values: list[str], current: str, editable: bool = False) -> QComboBox:
        combo = QComboBox()
        combo.addItems(values)
        combo.setEditable(editable)
        combo.setCurrentText(current)
        return combo

    def _build_layout(self) -> None:
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(22, 20, 22, 18)
        root.setSpacing(14)
        root.addWidget(self._build_header())
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(14)
        left_layout.addWidget(self._build_text_card(), 3)
        left_layout.addWidget(self._build_export_card(), 1)
        splitter.addWidget(left_column)
        splitter.addWidget(self._build_voice_card())
        splitter.setSizes([590, 510])
        root.addWidget(splitter, 1)
        root.addLayout(self._build_footer())

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(22, 16, 22, 16)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)
        title = QLabel(APP_NAME)
        title.setObjectName("appTitle")
        subtitle = QLabel("Estudio de locución latina · Beta")
        subtitle.setObjectName("appSubtitle")
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        self.status_pill = QLabel("Listo para generar")
        self.status_pill.setObjectName("statusPill")
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(self.status_pill, alignment=Qt.AlignmentFlag.AlignTop)
        return header

    def _build_text_card(self) -> QFrame:
        card, layout = self._card()
        layout.addLayout(self._heading("PASO 1 · GUIÓN", "Escribe tu narración", "Pega el texto o carga un archivo UTF-8. La preescucha rápida usa los primeros 260 caracteres."))
        self.text_widget = QTextEdit()
        self.text_widget.setPlaceholderText("Pega o escribe aquí el guión que quieres convertir en voz…")
        self.text_widget.setAcceptRichText(False)
        self.text_widget.textChanged.connect(self._update_text_metrics)
        layout.addWidget(self.text_widget, 1)
        metrics = QHBoxLayout()
        self.text_metrics = QLabel("0 palabras · 0 caracteres")
        self.text_metrics.setObjectName("muted")
        load_button = QPushButton("Cargar texto")
        load_button.clicked.connect(self.load_file)
        metrics.addWidget(self.text_metrics)
        metrics.addStretch()
        metrics.addWidget(load_button)
        layout.addLayout(metrics)
        return card

    def _build_voice_card(self) -> QScrollArea:
        scroll = QScrollArea()
        self.voice_scroll = scroll
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        card, layout = self._card()
        layout.addLayout(self._heading("PASO 2 · VOZ", "Define la locución", "Escoge un perfil y ajusta solo lo necesario. Los controles avanzados permanecen disponibles abajo."))
        basic = QGroupBox("Ajustes principales")
        form = QFormLayout(basic)
        form.setSpacing(10)
        self.profile_combo = self._combo(sorted(VOICE_PROFILES), DEFAULT_PROFILE)
        self.profile_combo.currentTextChanged.connect(self.apply_profile)
        self.voice_combo = self._combo(EDGE_VOICE_OPTIONS, EDGE_DEFAULT_VOICE, editable=True)
        self.rate_slider, self.rate_value = self._slider(130, 230, 176, " wpm")
        self.emotion_combo = self._combo(sorted(EMOTION_PRESETS), "neutro")
        form.addRow("Perfil", self.profile_combo)
        form.addRow("Voz latina", self.voice_combo)
        form.addRow("Velocidad", self._slider_row(self.rate_slider, self.rate_value))
        form.addRow("Emoción", self.emotion_combo)
        layout.addWidget(basic)
        advanced = QGroupBox("Ajustes avanzados")
        advanced_layout = QVBoxLayout(advanced)
        advanced_layout.setContentsMargins(10, 8, 10, 10)
        advanced_layout.addWidget(self._build_advanced_controls())
        layout.addWidget(advanced)
        layout.addStretch()
        scroll.setWidget(card)
        return scroll

    def _build_advanced_controls(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("advancedPanel")
        form = QFormLayout(widget)
        form.setContentsMargins(10, 14, 10, 10)
        form.setSpacing(10)
        self.provider_combo = self._combo(["edge", "local"], "edge")
        self.style_combo = self._combo(EDGE_STYLES, "narration-professional")
        self.delivery_combo = self._combo(sorted(DELIVERY_MODES), "podcast")
        self.mastering_combo = self._combo(sorted(MASTERING_PRESETS), DEFAULT_MASTERING_PRESET)
        self.pause_slider, self.pause_value = self._slider(0, 900, 250, " ms")
        self.volume_slider, self.volume_value = self._slider(50, 100, 100, "%")
        self.male_check = QCheckBox("Preferir voz masculina")
        self.male_check.setChecked(True)
        self.natural_mode_check = QCheckBox("Modo locutor natural (recomendado)")
        self.natural_mode_check.setChecked(True)
        form.addRow("Proveedor", self.provider_combo)
        form.addRow("Estilo de locución", self.style_combo)
        form.addRow("Modo de entrega", self.delivery_combo)
        form.addRow("Mastering", self.mastering_combo)
        form.addRow("Volumen", self._slider_row(self.volume_slider, self.volume_value))
        form.addRow("Pausa entre líneas", self._slider_row(self.pause_slider, self.pause_value))
        form.addRow("", self.male_check)
        form.addRow("", self.natural_mode_check)
        return widget

    def _slider(self, minimum: int, maximum: int, value: int, suffix: str) -> tuple[QSlider, QLabel]:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(value)
        label = QLabel(f"{value}{suffix}")
        label.setObjectName("valueLabel")
        slider.valueChanged.connect(lambda current: label.setText(f"{current}{suffix}"))
        return slider, label

    @staticmethod
    def _slider_row(slider: QSlider, label: QLabel) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(slider, 1)
        layout.addWidget(label)
        return row

    def _build_export_card(self) -> QFrame:
        card, layout = self._card()
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)
        layout.addLayout(self._heading("PASO 3 · EXPORTACIÓN", "Genera tu audio final", "Salida MP3 lista para guardar."))
        output_row = QGridLayout()
        output_row.setColumnStretch(1, 1)
        output_row.addWidget(QLabel("Destino MP3"), 0, 0)
        self.output_edit = QLineEdit(str(Path.cwd() / "salida_gui.mp3"))
        output_row.addWidget(self.output_edit, 0, 1)
        output_button = QPushButton("Cambiar…")
        output_button.clicked.connect(self.choose_output)
        output_row.addWidget(output_button, 0, 2)
        layout.addLayout(output_row)
        self.dictionary_toggle = QToolButton()
        self.dictionary_toggle.setText("Diccionario de pronunciación opcional")
        self.dictionary_toggle.setCheckable(True)
        self.dictionary_toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.dictionary_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(self.dictionary_toggle)
        self.dictionary_panel = QWidget()
        dictionary_row = QGridLayout(self.dictionary_panel)
        dictionary_row.setContentsMargins(0, 0, 0, 0)
        dictionary_row.setColumnStretch(1, 1)
        dictionary_row.addWidget(QLabel("Diccionario"), 0, 0)
        self.pronunciation_edit = QLineEdit(DEFAULT_PRONUNCIATION_FILE)
        dictionary_row.addWidget(self.pronunciation_edit, 0, 1)
        dictionary_button = QPushButton("Elegir…")
        dictionary_button.clicked.connect(self.choose_pronunciation_file)
        dictionary_row.addWidget(dictionary_button, 0, 2)
        layout.addWidget(self.dictionary_panel)
        self.dictionary_panel.setVisible(False)
        self.dictionary_toggle.toggled.connect(self._toggle_dictionary_panel)
        actions = QHBoxLayout()
        self.srt_check = QCheckBox("Crear subtítulos SRT")
        self.srt_check.setToolTip("Genera un archivo .srt sincronizado por frases junto al MP3.")
        layout.addWidget(self.srt_check)
        self.preview_quick_btn = QPushButton("Preescucha rápida")
        self.preview_quick_btn.setToolTip("Genera los primeros 260 caracteres sin mastering.")
        self.preview_quick_btn.clicked.connect(self.preview_quick_tts)
        self.preview_final_btn = QPushButton("Preescucha final")
        self.preview_final_btn.setToolTip("Genera una preescucha completa con mastering.")
        self.preview_final_btn.clicked.connect(self.preview_final_tts)
        history_btn = QPushButton("Historial")
        history_btn.setToolTip("Consulta los últimos renders sin guardar el guion.")
        history_btn.clicked.connect(self.show_render_history)
        self.convert_btn = QPushButton("Generar MP3")
        self.convert_btn.setObjectName("primaryButton")
        self.convert_btn.clicked.connect(self.run_tts)
        actions.addWidget(self.preview_quick_btn)
        actions.addWidget(self.preview_final_btn)
        actions.addWidget(history_btn)
        actions.addStretch()
        actions.addWidget(self.convert_btn)
        layout.addLayout(actions)
        status_row = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 1)
        self.status_label = QLabel("Listo para generar voz latina tipo locutor")
        self.status_label.setObjectName("muted")
        status_row.addWidget(self.progress, 1)
        status_row.addWidget(self.status_label)
        layout.addLayout(status_row)
        return card

    @Slot(bool)
    def _toggle_dictionary_panel(self, visible: bool) -> None:
        self.dictionary_panel.setVisible(visible)
        self.dictionary_toggle.setArrowType(
            Qt.ArrowType.DownArrow if visible else Qt.ArrowType.RightArrow
        )

    def _build_footer(self) -> QHBoxLayout:
        footer = QHBoxLayout()
        credit = QLabel(f"{COMPANY_NAME} · Desarrollado por {DEVELOPER_NAME} · Proyecto gratuito")
        credit.setObjectName("muted")
        support = QPushButton("Apoyar el proyecto")
        support.setObjectName("linkButton")
        support.clicked.connect(self.open_support_page)
        footer.addWidget(credit)
        footer.addStretch()
        footer.addWidget(support)
        return footer

    @Slot(str)
    def set_status(self, text: str) -> None:
        self.status_label.setText(text)
        self.status_pill.setText("Procesando…" if self._active_jobs else "Listo para generar")

    def _update_text_metrics(self) -> None:
        text = self.text_widget.toPlainText().strip()
        words = len(text.split()) if text else 0
        self.text_metrics.setText(f"{words:,} palabras · {len(text):,} caracteres")

    def _restore_preferences(self) -> None:
        preferences = load_preferences()
        profile = preferences.get("profile")
        if isinstance(profile, str) and profile in VOICE_PROFILES:
            self.profile_combo.setCurrentText(profile)
            self.apply_profile(profile)
        for name, combo in {"voice_hint": self.voice_combo, "provider": self.provider_combo, "style": self.style_combo, "delivery_mode": self.delivery_combo, "emotion": self.emotion_combo, "mastering_preset": self.mastering_combo}.items():
            value = preferences.get(name)
            if isinstance(value, str) and value:
                combo.setCurrentText(value)
        self.output_edit.setText(str(preferences.get("output", self.output_edit.text())))
        self.pronunciation_edit.setText(str(preferences.get("pronunciation_file", self.pronunciation_edit.text())))
        for name, widget in (("rate", self.rate_slider), ("volume", self.volume_slider), ("pause_ms", self.pause_slider)):
            value = preferences.get(name)
            if isinstance(value, (int, float)):
                widget.setValue(int(value))
        for name, widget in (("prefer_male", self.male_check), ("natural_mode", self.natural_mode_check)):
            value = preferences.get(name)
            if isinstance(value, bool):
                widget.setChecked(value)

    def _save_preferences(self) -> None:
        preferences = {
            "output": self.output_edit.text(), "profile": self.profile_combo.currentText(),
            "rate": self.rate_slider.value(), "volume": self.volume_slider.value(),
            "voice_hint": self.voice_combo.currentText(), "prefer_male": self.male_check.isChecked(),
            "provider": self.provider_combo.currentText(), "style": self.style_combo.currentText(),
            "pause_ms": self.pause_slider.value(), "natural_mode": self.natural_mode_check.isChecked(),
            "delivery_mode": self.delivery_combo.currentText(), "emotion": self.emotion_combo.currentText(),
            "pronunciation_file": self.pronunciation_edit.text(), "mastering_preset": self.mastering_combo.currentText(),
        }
        try:
            save_preferences(preferences)
        except OSError as exc:
            LOGGER.warning("No se pudieron guardar las preferencias: %s", exc)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._save_preferences()
        event.accept()

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        self.voice_scroll.verticalScrollBar().setValue(0)

    def open_support_page(self) -> None:
        support_url = os.getenv("STUDIO_TTS_DONATION_URL", PROJECT_WEBSITE)
        if not is_safe_support_url(support_url):
            LOGGER.warning("Se rechazo un enlace de apoyo invalido")
            QMessageBox.warning(self, "Enlace no válido", "El enlace de apoyo debe ser una dirección web HTTP o HTTPS.")
            return
        webbrowser.open(support_url)

    def load_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Abrir guión", "", "Texto (*.txt);;Todos (*.*)")
        if path:
            content = safe_read(path)
            if content:
                self.text_widget.setPlainText(content)
                self.set_status(f"Guión cargado: {Path(path).name}")

    def choose_output(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Guardar MP3", self.output_edit.text(), "Audio MP3 (*.mp3)")
        if path:
            self.output_edit.setText(str(Path(path).with_suffix(".mp3")))

    def choose_pronunciation_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Elegir diccionario", "", "JSON (*.json);;Todos (*.*)")
        if path:
            self.pronunciation_edit.setText(path)

    def show_render_history(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Historial de renders")
        dialog.resize(620, 320)
        layout = QVBoxLayout(dialog)
        entries = QListWidget()
        history = load_render_history()
        if not history:
            entries.addItem("Todavía no hay renders registrados.")
        else:
            for entry in reversed(history):
                created = str(entry.get("created_at", ""))
                output_name = str(entry.get("output_name", "salida.mp3"))
                profile = str(entry.get("profile", ""))
                voice = str(entry.get("voice", ""))
                provider = str(entry.get("provider", ""))
                entries.addItem(f"{created} · {output_name} · {profile} · {voice} ({provider})")
        layout.addWidget(entries)
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
        dialog.exec()

    @Slot(str)
    def apply_profile(self, name: str) -> None:
        profile = VOICE_PROFILES.get(name)
        if not profile:
            return
        self.rate_slider.setValue(int(profile.get("rate", self.rate_slider.value())))
        self.volume_slider.setValue(int(float(profile.get("volume", 1.0)) * 100))
        self.voice_combo.setCurrentText(str(profile.get("voice_hint", EDGE_DEFAULT_VOICE)))
        self.male_check.setChecked(bool(profile.get("prefer_male", self.male_check.isChecked())))
        self.style_combo.setCurrentText(str(profile.get("style", self.style_combo.currentText())))
        self.pause_slider.setValue(int(profile.get("pause_ms", self.pause_slider.value())))
        if hasattr(self, "status_label"):
            self.set_status(f"Perfil aplicado: {name}")

    def _collect_request(self) -> tuple[str, Path, dict]:
        text = self.text_widget.toPlainText().strip()
        if not text:
            raise ValueError("Escribe o carga texto para convertir.")
        output_path, audio_format = normalize_output_path(self.provider_combo.currentText(), Path(self.output_edit.text()).expanduser(), "mp3")
        self.output_edit.setText(str(output_path))
        params = {
            "rate": self.rate_slider.value(), "volume": self.volume_slider.value() / 100.0,
            "voice_hint": self.voice_combo.currentText().strip() or None,
            "prefer_male": self.male_check.isChecked(), "provider": self.provider_combo.currentText(),
            "audio_format": audio_format, "style": self.style_combo.currentText() or None,
            "pause_ms": self.pause_slider.value(), "profile": self.profile_combo.currentText(),
            "natural_mode": self.natural_mode_check.isChecked(), "delivery_mode": self.delivery_combo.currentText(),
            "emotion": self.emotion_combo.currentText(), "pronunciation_file": self.pronunciation_edit.text().strip() or None,
            "mastering_preset": self.mastering_combo.currentText(),
        }
        return text, output_path, params

    def _set_busy(self, busy: bool, *, exclusive: bool = False) -> None:
        if busy:
            self._active_jobs += 1
            self._export_active = self._export_active or exclusive
        else:
            self._active_jobs = max(0, self._active_jobs - 1)
            if exclusive:
                self._export_active = False
        self.convert_btn.setEnabled(not self._export_active)
        self.preview_quick_btn.setEnabled(not self._export_active)
        self.preview_final_btn.setEnabled(not self._export_active)
        self.progress.setRange(0, 0) if self._active_jobs else self.progress.setRange(0, 1)
        self.status_pill.setText("Procesando…" if self._active_jobs else "Listo para generar")

    @Slot(bool)
    def _finish_task(self, exclusive: bool) -> None:
        self._set_busy(False, exclusive=exclusive)

    def preview_quick_tts(self) -> None:
        self._preview_tts(final_quality=False)

    def preview_final_tts(self) -> None:
        self._preview_tts(final_quality=True)

    def _preview_tts(self, final_quality: bool) -> None:
        try:
            text, _, params = self._collect_request()
        except Exception as exc:
            QMessageBox.warning(self, "Sin texto", str(exc))
            return
        if not final_quality:
            text = " ".join(text.split())[:260]
            if not text:
                QMessageBox.warning(self, "Sin texto", "No hay texto suficiente para preescucha.")
                return
        preview_path = create_preview_path(final_quality)
        self._set_busy(True)
        self.set_status("Generando preescucha final…" if final_quality else "Generando preescucha rápida…")

        def worker() -> None:
            try:
                synthesize(text, preview_path, enable_mastering=final_quality, **params)
                self.status_requested.emit(f"Preescucha lista: {preview_path.name}")
                self.preview_ready.emit(str(preview_path))
            except Exception as exc:
                LOGGER.exception("Error durante la preescucha")
                self.error_requested.emit("Error en preescucha", str(exc))
                self.status_requested.emit("Error en preescucha")
            finally:
                self.task_finished.emit(False)
        threading.Thread(target=worker, daemon=True).start()

    def run_tts(self) -> None:
        try:
            text, output_path, params = self._collect_request()
        except Exception as exc:
            QMessageBox.warning(self, "Sin texto", str(exc))
            return
        if params["provider"] == "local" and not has_ffmpeg():
            QMessageBox.warning(self, "FFmpeg requerido", "Para usar el proveedor local con salida MP3, instala FFmpeg o cambia a proveedor Edge.")
            return
        create_srt = self.srt_check.isChecked()
        self._set_busy(True, exclusive=True)
        self.set_status("Generando audio profesional…")

        def worker() -> None:
            try:
                synthesize(text, output_path, enable_mastering=True, **params)
                try:
                    append_render_history({
                        "output_name": output_path.name,
                        "provider": params.get("provider"),
                        "profile": params.get("profile"),
                        "voice": params.get("voice_hint"),
                        "duration_seconds": 0.0,
                    })
                except OSError as exc:
                    LOGGER.warning("No se pudo guardar el historial del render: %s", exc)
                message = f"Exportado MP3: {output_path.name}"
                if create_srt:
                    subtitle_path = output_path.with_suffix(".srt")
                    try:
                        write_srt(text, output_path, subtitle_path)
                        message += f" · SRT: {subtitle_path.name}"
                    except (OSError, ValueError) as exc:
                        LOGGER.warning("No se pudo generar el SRT: %s", exc)
                if not has_ffmpeg():
                    message += " (sin mastering: FFmpeg no instalado)"
                self.status_requested.emit(message)
            except Exception as exc:
                LOGGER.exception("Error durante la exportación")
                self.error_requested.emit("Error al exportar", str(exc))
                self.status_requested.emit("Error al exportar")
            finally:
                self.task_finished.emit(True)
        threading.Thread(target=worker, daemon=True).start()

    @Slot(str, str)
    def _show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, f"No se pudo completar la operación:\n{message}")

    @Slot(str)
    def _open_preview(self, path: str) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))


def main() -> int:
    configure_logging()
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
    window = TTSApp()
    window.show()
    screen = window.screen() or app.primaryScreen()
    if screen:
        window.move(screen.availableGeometry().center() - window.frameGeometry().center())
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
