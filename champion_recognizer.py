import cv2
import numpy as np
import os
import requests
from skimage.metrics import structural_similarity as ssim

class ChampionRecognizer:
    BASE_URL = 'https://127.0.0.1:2999'
    PLAYER_LIST_ENDPOINT = '/liveclientdata/playerlist'
    
    def __init__(self):
        self.champion_images = {}
        self.lower_red = np.array([100, 0, 0])
        self.upper_red = np.array([255, 100, 100])
        self.load_champion_images()

    def load_champion_images(self, champion_names=None):
        base_path = "champion_icons"
        if champion_names is None:
            champion_names = [os.path.splitext(file)[0] for file in os.listdir(base_path) if file.endswith(".png")]
        for champ_name in champion_names:
            file_name = f"{champ_name}.png"
            champ_img = cv2.imread(os.path.join(base_path, file_name))
            if champ_img is not None:
                self.champion_images[champ_name] = champ_img

    def fetch_opponent_champions(self):
        try:
            response = requests.get(f"{self.BASE_URL}{self.PLAYER_LIST_ENDPOINT}", verify=False)
            response.raise_for_status()
            player_list = response.json()
            opponents = [player['championName'] for player in player_list if player['team'] != 'ORDER']
            self.champion_images = {}
            self.load_champion_images(opponents)
        except requests.exceptions.RequestException:
            print("Failed to fetch opponent champions from API.")
            self.champion_images = {}

    def calculate_ssim_score(self, img1, img2):
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        score, _ = ssim(img1, img2, full=True)
        return score

    def find_best_match(self, circle_img):
        best_match = None
        highest_score = 0.3
        for champ_name, champ_img in self.champion_images.items():
            champ_resized = cv2.resize(champ_img, (circle_img.shape[1], circle_img.shape[0]))
            score = self.calculate_ssim_score(circle_img, champ_resized)
            if score > highest_score:
                highest_score = score
                best_match = champ_name
        return best_match, highest_score

    def detect_champions(self, img, circles):
        detected_champions = []
        if circles is not None and len(circles) > 0:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                if 12 <= r <= 40:
                    circle_img = img[y - r:y + r, x - r:x + r]
                    if circle_img.size > 0:
                        champion_name, ssim_score = self.find_best_match(circle_img)
                        if champion_name:
                            detected_champions.append((champion_name, x, y, ssim_score))
        return detected_champions
