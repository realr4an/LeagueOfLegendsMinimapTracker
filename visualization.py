import cv2
import numpy as np

class Visualization:
    def __init__(self):
        self.lower_white = np.array([200, 200, 200])
        self.upper_white = np.array([255, 255, 255])

    def draw_circle(self, img, x, y, r, champion_name):
        cv2.circle(img, (x, y), r, (0, 255, 0), 2)
        cv2.putText(img, champion_name, (x + r + 5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    def draw_arrow(self, img, start, end):
        cv2.arrowedLine(img, start, end, (0, 255, 255), 2, tipLength=0.3)

    def find_rectangles(self, img):
        rectangle_center = None
        mask_white = cv2.inRange(img, self.lower_white, self.upper_white)
        kernel = np.ones((3, 3), np.uint8)
        mask_white = cv2.dilate(mask_white, kernel, iterations=2)
        mask_white = cv2.erode(mask_white, kernel, iterations=1)
        contours, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if 60 < w < 160 and 20 < h < 100:
                rectangle_center = (x + w // 2, y + h // 2)
        return rectangle_center

    def visualize(self, img, champions, rectangle_center):
        for champion_name, x, y in champions:
            self.draw_circle(img, x, y, 20, champion_name)
            if rectangle_center:
                self.draw_arrow(img, rectangle_center, (x, y))
