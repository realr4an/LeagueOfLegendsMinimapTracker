from champion_tracker import ChampionTracker
from config_loader import load_config
from overlay import TransparentOverlay
from PyQt5.QtWidgets import QApplication
import sys
import threading
import keyboard
from control_panel import ControlPanel
from PyQt5.QtGui import QColor
from config_loader import save_config

if __name__ == "__main__":
    cfg = load_config()
    monitor_config = {
        "top": int(cfg.get("top", 850)),
        "left": int(cfg.get("left", 1500)),
        "width": int(cfg.get("width", 240)),
        "height": int(cfg.get("height", 240)),
    }
    start_team = str(cfg.get("team", "CHAOS")).upper()
    start_color_hex = str(cfg.get("overlay_color", "#ff0000"))

    tracker = ChampionTracker(monitor_config)
    tracker.set_team_mode(start_team)

    app = QApplication(sys.argv)

    overlay = TransparentOverlay(
        lambda: tracker.get_latest_positions(),
        lambda: tracker.get_rectangle_center(),
        monitor_config
    )
    overlay.set_overlay_color(QColor(start_color_hex))

    def apply_size_cb(new_cfg: dict):
        tracker.monitor.update(new_cfg)
        overlay.update_minimap_config(new_cfg)

    def apply_color_cb(qcolor: QColor):
        overlay.set_overlay_color(qcolor)

    def apply_team_cb(mode: str):
        tracker.set_team_mode(mode)
        print(f"Teammodus gesetzt auf: {mode}")

    def apply_save_cb(snapshot: dict):
        # snapshot enthält top/left/width/height/overlay_color/team
        save_config(snapshot)          # schreibt nach config.txt
        print("Settings gespeichert.")

    # --- Callbacks fürs Panel ---
    def apply_size_cb(new_cfg: dict):
        # Tracker liest self.monitor in jeder Iteration – dict updaten reicht
        tracker.monitor.update(new_cfg)
        # Overlay über Setter informieren (falls du später mal eine Kopie übergibst)
        overlay.update_minimap_config(new_cfg)

    def apply_color_cb(qcolor: QColor):
        overlay.set_overlay_color(qcolor)

    panel = ControlPanel(monitor_config, apply_size_cb, apply_color_cb, apply_team_cb,
                     QColor(start_color_hex), start_team, apply_save_cb)
    panel.show()

    # Rest (Hotkey, Threads) bleibt wie gehabt ...
    def on_save_key_pressed():
        tracker.save_timeline_to_csv()
        tracker.print_recognition_stats()
        print("Timeline saved via keybind.")

    keyboard.add_hotkey('ctrl+s', on_save_key_pressed)

    def start_tracker():
        tracker.capture_and_process()

    tracker_thread = threading.Thread(target=start_tracker, daemon=True)
    tracker_thread.start()

    overlay.show()
    sys.exit(app.exec_())
