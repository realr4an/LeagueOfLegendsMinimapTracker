from champion_tracker import ChampionTracker
from config_loader import load_config
from overlay import TransparentOverlay
from PyQt5.QtWidgets import QApplication
import sys
import threading
import keyboard


if __name__ == "__main__":
    # Load configuration
    config = load_config()
    monitor_config = {
        "top": config.get("top", 850),
        "left": config.get("left", 1500),
        "width": config.get("width", 240),
        "height": config.get("height", 240),
    }

    # Initialize ChampionTracker
    tracker = ChampionTracker(monitor_config)
    tracker.fetch_static_champions()  # Load champions only from the API

    # Start PyQt5 application
    app = QApplication(sys.argv)

    # Initialize the overlay
    overlay = TransparentOverlay(
        lambda: tracker.get_latest_positions(),
        lambda: tracker.get_rectangle_center(),
        monitor_config  # Pass minimap config to the overlay
    )

    def on_save_key_pressed():
        tracker.save_timeline_to_csv()
        tracker.print_recognition_stats()
        print("Timeline saved via keybind.")

    keyboard.add_hotkey('ctrl+s', on_save_key_pressed)


    # Run tracker and overlay
    def start_tracker():
        tracker.capture_and_process()

    tracker_thread = threading.Thread(target=start_tracker, daemon=True)
    tracker_thread.start()

    overlay.show()
    sys.exit(app.exec_())
