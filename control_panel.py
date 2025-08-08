# control_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSlider, QPushButton,
    QColorDialog, QHBoxLayout, QApplication, QComboBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

class ControlPanel(QWidget):
    def __init__(self, monitor_config, apply_size_cb, apply_color_cb, apply_team_cb,
                 initial_color: QColor, initial_team: str, save_cb):
        super().__init__()
        self.monitor_config = monitor_config
        self.apply_size_cb = apply_size_cb
        self.apply_color_cb = apply_color_cb
        self.apply_team_cb = apply_team_cb
        self.save_cb = save_cb
        self.current_color = initial_color
        self.initial_team = (initial_team or "CHAOS").upper()
        self._drag_offset = QPoint()
        self._init_ui()


    def _init_ui(self):
        # Fenster-Flags
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Karte (Wrapper) mit runden Ecken + Shadow
        wrapper = QWidget(self)
        wrapper.setObjectName("card")
        wrapper.setStyleSheet("""
            QWidget#card { background: #202225; border-radius: 14px; }
            QLabel { color: #e6e6e6; }
            QPushButton {
                background: #2b2e33; color: #e6e6e6; border: 1px solid #3a3d42;
                border-radius: 8px; padding: 6px 10px;
            }
            QPushButton:hover { background: #34383e; }
            QSlider::groove:horizontal { height: 6px; background: #2f3136; border-radius: 3px; }
            QSlider::handle:horizontal { width: 14px; background: #7289da; margin: -6px 0; border-radius: 7px; }
            QComboBox { background:#2b2e33; color:#e6e6e6; border:1px solid #3a3d42; border-radius:8px; padding:4px 6px; }
            QComboBox QAbstractItemView { background:#2b2e33; color:#e6e6e6; selection-background-color:#34383e; }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        wrapper.setGraphicsEffect(shadow)

        # >>> HIER das Layout anlegen und als Attribut merken <<<
        self.vbox = QVBoxLayout(wrapper)
        self.vbox.setContentsMargins(16, 12, 16, 16)

        # Header
        top = QHBoxLayout()
        title = QLabel("Minimap-Einstellungen")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("QPushButton{background:transparent;border:none;color:#bbb;} QPushButton:hover{color:#fff;}")
        top.addWidget(title)
        top.addStretch(1)
        top.addWidget(close_btn)
        self.vbox.addLayout(top)

        # Team-Auswahl
        self.vbox.addWidget(QLabel("Team"))
        self.team_combo = QComboBox()
        self.team_combo.addItems(["Gegner (auto)", "ORDER (Blau)", "CHAOS (Rot)"])
        # initialer Wert (falls du im __init__ self.initial_team gesetzt hast)
        try:
            idx = 0 if self.initial_team == "OPPONENT" else (1 if self.initial_team == "ORDER" else 2)
            self.team_combo.setCurrentIndex(idx)
        except AttributeError:
            pass
        self.team_combo.currentIndexChanged.connect(self._on_team_changed)
        self.vbox.addWidget(self.team_combo)

        # Größe
        self.vbox.addWidget(QLabel("Größe (px)"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(150)
        self.size_slider.setMaximum(600)
        self.size_slider.setValue(int(self.monitor_config.get("width", 240)))
        self.size_slider.valueChanged.connect(self._on_size_changed)
        self.vbox.addWidget(self.size_slider)

        # Farbe
        color_row = QHBoxLayout()
        self.color_preview = QLabel(" Overlay-Farbe ")
        self.color_preview.setFixedHeight(26)
        # falls du im __init__ self.current_color gesetzt hast:
        try:
            self.color_preview.setStyleSheet(f"background:{self.current_color.name()};border-radius:6px;color:#111;padding:4px 8px;")
        except AttributeError:
            self.color_preview.setStyleSheet("background:#ff0000;border-radius:6px;color:#111;padding:4px 8px;")
        pick_btn = QPushButton("Farbe wählen")
        pick_btn.clicked.connect(self._pick_color)
        color_row.addWidget(self.color_preview, 1)
        color_row.addWidget(pick_btn, 0)
        self.vbox.addLayout(color_row)

        # Speichern
        save_btn = QPushButton("Speichern")
        save_btn.clicked.connect(self._on_save_clicked)
        self.vbox.addWidget(save_btn)

        # Größe & Position des Panels
        self.resize(320, 210)
        self.move(60, 60)

        # Root-Layout (transparenter Hintergrund)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(wrapper)


    def _on_save_clicked(self):
        snapshot = {
            "top": self.monitor_config.get("top", 850),
            "left": self.monitor_config.get("left", 1500),
            "width": self.monitor_config.get("width", 240),
            "height": self.monitor_config.get("height", 240),
            "overlay_color": self.current_color.name(),
            "team": ("OPPONENT" if self.team_combo.currentIndex() == 0
                     else ("ORDER" if self.team_combo.currentIndex() == 1 else "CHAOS"))
        };
        self.save_cb(snapshot)

    # ---- Dragging (Fenster verschiebbar) ----
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_offset)
            event.accept()

    # ---- Callbacks ----
    def _on_team_changed(self, idx: int):
        mode = "OPPONENT" if idx == 0 else ("ORDER" if idx == 1 else "CHAOS")
        self.apply_team_cb(mode)

    def _on_size_changed(self, v: int):
        # unten-rechts verankern (20 px Margin)
        screen = QApplication.primaryScreen().size()
        left = max(0, screen.width() - v - 20)
        top = max(0, screen.height() - v - 20)
        self.monitor_config.update({"left": left, "top": top, "width": v, "height": v})
        self.apply_size_cb(dict(self.monitor_config))

    def _pick_color(self):
        col = QColorDialog.getColor(parent=self, title="Overlay-Farbe wählen")
        if col.isValid():
            self.color_preview.setStyleSheet(f"background:{col.name()};border-radius:6px;color:#111;padding:4px 8px;")
            self.apply_color_cb(col)
