import cv2
import numpy as np
import os
import requests
from skimage.metrics import structural_similarity as ssim
import urllib3
import threading
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ChampionRecognizer:
    BASE_URL = 'https://127.0.0.1:2999'
    PLAYER_LIST_ENDPOINT = '/liveclientdata/playerlist'
    
    def __init__(self):
        self._icons_lock = threading.RLock()
        self.champion_images = {}
        self.lower_red = np.array([100, 0, 0])
        self.upper_red = np.array([255, 100, 100])
        self.team_mode = "CHAOS"  
        self.load_champion_images()
        

    def set_team_mode(self, mode: str):
        mode = (mode or "").upper()
        self.team_mode = mode if mode in ("OPPONENT", "ORDER", "CHAOS") else "OPPONENT"


    def load_champion_images(self, champion_names=None):
        base_path = "champion_icons"
        if champion_names is None:
            champion_names = [os.path.splitext(file)[0] for file in os.listdir(base_path) if file.endswith(".png")]

        tmp = {}
        for champ_name in champion_names:
            file_name = f"{champ_name}.png"
            champ_img = cv2.imread(os.path.join(base_path, file_name))
            if champ_img is not None:
                tmp[champ_name] = champ_img

        # atomarer Swap unter Lock
        with self._icons_lock:
            self.champion_images = tmp


    def fetch_opponent_champions(self):
        """
        Lädt Champion-Icons für das gewählte Team.
        team_mode="OPPONENT": ermittelt eigenes Team und nimmt das gegnerische.
        team_mode="ORDER"/"CHAOS": nimmt exakt dieses Team.
        """
        try:
            # Team bestimmen
            if self.team_mode in ("ORDER", "CHAOS"):
                team_to_fetch = self.team_mode
            else:
                active = requests.get(f"{self.BASE_URL}/liveclientdata/activeplayer",
                                    verify=False, timeout=1.0)
                active.raise_for_status()
                my_team = active.json().get('team')
                team_to_fetch = 'CHAOS' if my_team == 'ORDER' else 'ORDER'

            # Alle Spieler holen und client-seitig filtern
            resp = requests.get(f"{self.BASE_URL}{self.PLAYER_LIST_ENDPOINT}",
                                verify=False, timeout=1.0)
            resp.raise_for_status()
            players = resp.json()
            names = [p['championName'] for p in players if p.get('team') == team_to_fetch]
            self.load_champion_images(names)  # macht den atomaren Swap


            # Nur diese Icons laden
            self.champion_images = {}
            self.load_champion_images(names)
            print(f"Geladene Champions ({team_to_fetch}): {', '.join(names) if names else '—'}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch champions from API: {e}. Fallback auf lokale Icons.")
            # Optionaler Fallback:
            # self.champion_images = {}
            # self.load_champion_images()

    def _icon_items_snapshot(self):
        with self._icons_lock:
            return list(self.champion_images.items())

    def calculate_ssim_score(self, img1, img2):
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        score, _ = ssim(img1, img2, full=True)
        return score

    def find_best_match(self, circle_img):
        best_match = None
        highest_score = 0.3
        for champ_name, champ_img in self._icon_items_snapshot():
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
