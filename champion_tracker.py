import mss
import cv2
import numpy as np
import pandas as pd
import csv
import os
import time
from datetime import datetime
from champion_recognizer import ChampionRecognizer
from visualization import Visualization

class ChampionTracker:
    
    def __init__(self, monitor_config):
        self.monitor = monitor_config
        self.recognizer = ChampionRecognizer()
        self.visualizer = Visualization()
        self.latest_positions = {}
        self.champions = []
        self.rectangle_center = None
        self.timeline_positions = []
        self.last_save_time = 0
        self.recognition_stats = {
            "total_recognitions": 0,
            "successful_recognitions": 0,
            "low_ssim_recognitions": 0,
            "average_ssim": 0.0,
        }


    def save_position_to_timeline(self):
        for champ_name, pos in self.latest_positions.items():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if pos:  # Stelle sicher, dass X und Y vorhanden sind
                self.timeline_positions.append({
                    "timestamp": timestamp,
                    "champion": champ_name,
                    "X": int(pos["X"]),
                    "Y": int(pos["Y"])
                })
                print(f"Added to timeline: {champ_name} at ({int(pos['X'])}, {int(pos['Y'])}) ({timestamp})")



    def save_timeline_to_csv(self, file_path="timeline.csv"):
        if not self.timeline_positions:
            print("No timeline positions to save.")
            return

        file_exists = os.path.isfile(file_path)
        with open(file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["timestamp", "champion", "X", "Y"])
            if not file_exists:
                writer.writeheader()
            writer.writerows(self.timeline_positions)
        print(f"Timeline saved to {file_path}")
        self.timeline_positions.clear()

    def print_recognition_stats(self):
        print("\n--- Champion Recognition Statistics ---")
        print(f"Total Recognitions: {self.recognition_stats['total_recognitions']}")
        print(f"Successful Recognitions: {self.recognition_stats['successful_recognitions']}")
        print(f"Low SSIM Recognitions (<0.5): {self.recognition_stats['low_ssim_recognitions']}")
        print(f"Average SSIM: {self.recognition_stats['average_ssim']:.2f}")
        print("--------------------------------------")


    def fetch_static_champions(self):
        """
        Fetch the list of champions from the API and set them as static names.
        Only opponent champions will be considered.
        """
        self.recognizer.fetch_opponent_champions()
        self.champions = list(self.recognizer.champion_images.keys())

    def get_latest_positions(self):
        """
        Return a list of champion names and their positions.
        If a position is not available, set it to None.
        """
        return [
            {"Champion": champ, "Position": self.latest_positions.get(champ, None)}
            for champ in self.champions
        ]
    
    def get_rectangle_center(self):
        return self.rectangle_center

    def capture_and_process(self):
        """
        Continuously captures and processes the screen to update champion positions.
        """
        self.fetch_static_champions()  # Fetch static names at the start

        with mss.mss() as sct:
            total_ssim = 0
            while True:
                screen_img = sct.grab(self.monitor)
                img = np.array(screen_img)
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                self.rectangle_center = self.visualizer.find_rectangles(img)
                mask_red = cv2.inRange(img, self.recognizer.lower_red, self.recognizer.upper_red)
                mask_red_blurred = cv2.GaussianBlur(mask_red, (3, 3), 2)
                circles = cv2.HoughCircles(mask_red_blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20, param1=50, param2=30, minRadius=10, maxRadius=100)

                champions = self.recognizer.detect_champions(img, circles)

                for champ_name, x, y, ssim_score in champions:
                    self.latest_positions[champ_name] = {"X": x, "Y": y}
                    self.recognition_stats["total_recognitions"] += 1
                    total_ssim += ssim_score
                    if ssim_score < 0.4:
                        self.recognition_stats["low_ssim_recognitions"] += 1
                    else:
                        self.recognition_stats["successful_recognitions"] += 1

                if self.recognition_stats["successful_recognitions"] > 0:
                    self.recognition_stats["average_ssim"] = (
                        total_ssim / self.recognition_stats["total_recognitions"]
                    )
                

                current_time = time.time()
                if current_time - self.last_save_time >= 1:
                    self.save_position_to_timeline()
                    self.last_save_time = current_time
