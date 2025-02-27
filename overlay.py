from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
import math

class TransparentOverlay(QMainWindow):
    def __init__(self, get_data_callback, get_rectangle_center_callback, minimap_config):
        """
        Transparent overlay for displaying champion data, arrows, and the minimap box.
        :param get_data_callback: Function to fetch champion data.
        :param get_rectangle_center_callback: Function to fetch the center of the white rectangle.
        :param minimap_config: Dictionary containing 'top', 'left', 'width', and 'height' for the minimap.
        """
        super().__init__()
        self.get_data_callback = get_data_callback
        self.get_rectangle_center_callback = get_rectangle_center_callback
        self.minimap_config = minimap_config
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setGeometry(0, 0, QApplication.primaryScreen().size().width(), QApplication.primaryScreen().size().height())
        self.data = []
        self.rectangle_center = None

        # Timer for updating the overlay
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_overlay)
        self.timer.start(100)

    def update_overlay(self):
        self.data = self.get_data_callback()
        self.rectangle_center = self.get_rectangle_center_callback()
        self.update()

    def paintEvent(self, event):
        """
        Draw the champion names, arrows, and the minimap box on the overlay.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the red box for the minimap
        minimap_top = self.minimap_config.get("top", 850)
        minimap_left = self.minimap_config.get("left", 1500)
        minimap_width = self.minimap_config.get("width", 240)
        minimap_height = self.minimap_config.get("height", 240)

        painter.setPen(QColor(255, 0, 0, 255))  # Red border
        painter.drawRect(minimap_left, minimap_top, minimap_width, minimap_height)

        # Get screen center
        screen_width = self.width()
        screen_height = self.height()
        screen_center = (screen_width // 2, screen_height // 2)

        # Draw champion names and positions
        y_offset = 20
        for entry in self.data:
            name = entry.get("Champion", "Unknown")
            position = entry.get("Position", None)

            # Combine name and position
            if position is not None:
                text = f"{name} - ({position['X']}, {position['Y']})"
            else:
                text = f"{name} - (-)"

            # Draw the text
            painter.setPen(QColor(255, 255, 255, 255))
            painter.drawText(10, y_offset, text)
            y_offset += 20

            # Draw arrows if position is available
            if position is not None and self.rectangle_center:
                rect_x, rect_y = self.rectangle_center

                # Calculate the arrow end point and distance
                arrow_end = (screen_center[0] + (position['X'] - rect_x), screen_center[1] + (position['Y'] - rect_y))
                distance = math.sqrt((position['X'] - rect_x) ** 2 + (position['Y'] - rect_y) ** 2)

                # Draw the arrow
                painter.setPen(QColor(255, 0, 0, 255))  # Red color for arrow
                painter.setBrush(QColor(255, 0, 0, 255))  # Ensure the arrow is visible
                painter.setPen(QColor(255, 0, 0, 255))
                painter.drawLine(screen_center[0], screen_center[1], arrow_end[0], arrow_end[1])

                # Draw the name and distance near the arrow
                label = f"{name} ({int(distance)})"
                painter.setPen(QColor(255, 255, 255, 255))  # White color for text
                painter.drawText(arrow_end[0] + 5, arrow_end[1] - 5, label)
