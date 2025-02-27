import cv2
import numpy as np
import mss
import os
import requests
from skimage.metrics import structural_similarity as ssim
import pandas as pd
from datetime import datetime

BASE_URL = 'https://127.0.0.1:2999'
PLAYER_LIST_ENDPOINT = '/liveclientdata/playerlist'
monitor = {"top": 1250, "left": 2300, "width": 550, "height": 550}
lower_red = np.array([100, 0, 0])
upper_red = np.array([255, 100, 100])
lower_white = np.array([200, 200, 200])
upper_white = np.array([255, 255, 255])
champion_images = {}

def load_champion_images(champion_names=None):
    base_path = "champion_icons"
    if champion_names is None:
        champion_names = [os.path.splitext(file)[0] for file in os.listdir(base_path) if file.endswith(".png")]
    for champ_name in champion_names:
        file_name = f"{champ_name}.png"
        champ_img = cv2.imread(os.path.join(base_path, file_name))
        if champ_img is not None:
            champion_images[champ_name] = champ_img

def fetch_opponent_champions():
    try:
        response = requests.get(f"{BASE_URL}{PLAYER_LIST_ENDPOINT}", verify=False)
        response.raise_for_status()
        player_list = response.json()
        opponents = [player['championName'] for player in player_list if player['team'] != 'ORDER']
        load_champion_images(opponents)
    except requests.exceptions.RequestException:
        load_champion_images()

def calculate_ssim_score(img1, img2):
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(img1, img2, full=True)
    return score

def find_best_match(circle_img):
    best_match = None
    highest_score = 0.2
    for champ_name, champ_img in champion_images.items():
        champ_resized = cv2.resize(champ_img, (circle_img.shape[1], circle_img.shape[0]))
        score = calculate_ssim_score(circle_img, champ_resized)
        if score > highest_score:
            highest_score = score
            best_match = champ_name
    return best_match

def draw_arrow(img, start, end):
    color = (0, 255, 255)
    thickness = 2
    cv2.arrowedLine(img, start, end, color, thickness, tipLength=0.3)

def capture_and_display():
    fetch_opponent_champions()
    df = pd.DataFrame(columns=["Timestamp", "Champion", "X", "Y"])
    with mss.mss() as sct:
        while True:
            screen_img = sct.grab(monitor)
            img = np.array(screen_img)
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

            mask_red = cv2.inRange(img, lower_red, upper_red)
            cv2.imshow("Mask", mask_red)
            mask_red_blurred = cv2.GaussianBlur(mask_red, (3, 3), 2)
            cv2.imshow("Mask Blurred", mask_red_blurred)
            circles = cv2.HoughCircles(mask_red_blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20, param1=50, param2=30, minRadius=23, maxRadius=40)

            rectangle_center = None
            mask_white = cv2.inRange(img, lower_white, upper_white)
            kernel = np.ones((3, 3), np.uint8)
            mask_white = cv2.dilate(mask_white, kernel, iterations=2)
            mask_white = cv2.erode(mask_white, kernel, iterations=1)
            contours, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if 80 < w < 260 and 50 < h < 200:
                    rectangle_center = (x + w // 2, y + h // 2)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if circles is not None and len(circles) > 0:
                circles = np.round(circles[0, :]).astype("int")
                for (x, y, r) in circles:
                    if 12 <= r <= 40:
                        circle_img = img[y-r:y+r, x-r:x+r]
                        if circle_img.size > 0:
                            champion_name = find_best_match(circle_img)
                            cv2.circle(img, (x, y), r, (0, 255, 255), 2)
                            if champion_name and rectangle_center:
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                df = pd.concat([df, pd.DataFrame([{"Timestamp": timestamp, "Champion": champion_name, "X": int(x), "Y": int(y)}])], ignore_index=True)
                                cv2.putText(img, champion_name, (x + r + 5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                # draw_arrow(img, rectangle_center, (x, y))

            cv2.imshow("Detected Circles", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    df.to_csv("champion_positions.csv", index=False)
    cv2.destroyAllWindows()

capture_and_display()
