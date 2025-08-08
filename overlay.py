from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
import math

class TransparentOverlay(QMainWindow):
    def __init__(self, get_data_callback, get_rectangle_center_callback, minimap_config):
        super().__init__()
        self.get_data_callback = get_data_callback
        self.get_rectangle_center_callback = get_rectangle_center_callback
        self.minimap_config = minimap_config
        self.overlay_color = QColor(255, 0, 0, 255)  # NEU: Standardfarbe
        self.init_ui()
        self.fade_seconds = 10

    # NEU: Setter für Farbe
    def set_overlay_color(self, color: QColor):
        self.overlay_color = color
        self.update()

    def _blend(self, c_from: QColor, c_to: QColor, t: float) -> QColor:
        t = max(0.0, min(1.0, float(t)))
        r = int(c_from.red()   * (1 - t) + c_to.red()   * t)
        g = int(c_from.green() * (1 - t) + c_to.green() * t)
        b = int(c_from.blue()  * (1 - t) + c_to.blue()  * t)
        a = int(c_from.alpha() * (1 - t) + c_to.alpha() * t)
        return QColor(r, g, b, a)


    # NEU: Setter für Minimap-Config
    def update_minimap_config(self, cfg: dict):
        self.minimap_config = cfg
        self.update()

    def paintEvent(self, event):
        """
        Draw the champion names, arrows, and the minimap box on the overlay.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Minimap-Box (Screen-Koords)
        minimap_top = self.minimap_config.get("top", 850)
        minimap_left = self.minimap_config.get("left", 1500)
        minimap_width = self.minimap_config.get("width", 240)
        minimap_height = self.minimap_config.get("height", 240)

        # Rahmen in der gewählten Overlay-Farbe
        painter.setPen(self.overlay_color)
        painter.drawRect(minimap_left, minimap_top, minimap_width, minimap_height)

        # Bildschirmmitte (Startpunkt der Pfeile)
        screen_center = (self.width() // 2, self.height() // 2)

        # ---- Liste: Champion + Position ----
        y_offset = 20
        for entry in self.data:
            name = entry.get("Champion", "Unknown")
            position = entry.get("Position")
            last_seen_secs = entry.get("last_seen_secs")  # neu

            # Fading: Weiß -> Overlay-Farbe je Sekunde ohne Erkennung
            if position is None:
                t = 1.0  # nie/aktuell nicht erkannt -> sofort stark einfärben
            else:
                # wenn gesehen, ist last_seen_secs 0; sonst z.B. 1,2,3...
                if isinstance(last_seen_secs, int) and last_seen_secs > 0:
                    t = min(1.0, last_seen_secs / self.fade_seconds)
                else:
                    t = 0.0

            text_color = self._blend(QColor(255, 255, 255, 255), self.overlay_color, t)

            text = f"{name} - ({position['X']}, {position['Y']})" if position else f"{name} - (-)"
            painter.setPen(text_color)
            painter.drawText(10, y_offset, text)
            y_offset += 20

        # ---- Pfeile: Bildschirmmitte -> screen_center + (pos - rect_center_local) ----
        # rect_center_local ist in Minimap-Koords; wenn None, nimm Minimap-Mitte
        rect_center_local = self.rectangle_center
        if rect_center_local is None:
            rect_center_local = (minimap_width // 2, minimap_height // 2)

        for entry in self.data:
            position = entry.get("Position")
            if not position:
                continue

            # Delta in Minimap-Koords
            dx = int(position['X']) - int(rect_center_local[0])
            dy = int(position['Y']) - int(rect_center_local[1])

            # Endpunkt in Screen-Koords
            end_x = screen_center[0] + dx
            end_y = screen_center[1] + dy

            # Linie + Label
            painter.setPen(self.overlay_color)
            painter.drawLine(screen_center[0], screen_center[1], end_x, end_y)

            dist = int(math.hypot(dx, dy))  # Distanz in Minimap-Pixeln
            painter.setPen(QColor(255, 255, 255, 255))
            painter.drawText(end_x + 5, end_y - 5, f"{entry.get('Champion', 'Unknown')} ({dist})")



    def init_ui(self):
        # transparentes Vollbild-Overlay
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        screen = QApplication.primaryScreen().size()
        self.setGeometry(0, 0, screen.width(), screen.height())

        # Startwerte
        self.data = []
        self.rectangle_center = None

        # Timer für regelmäßiges Redraw
        self._timer = QTimer(self)
        self._timer.setInterval(100)  # alle 100ms
        self._timer.timeout.connect(self.update_overlay)
        self._timer.start()

    def update_overlay(self):
        # Daten vom Tracker holen
        try:
            self.data = self.get_data_callback() or []
        except Exception:
            self.data = []
        try:
            self.rectangle_center = self.get_rectangle_center_callback()
        except Exception:
            self.rectangle_center = None
        self.update()
