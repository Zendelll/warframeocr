import cv2
import numpy as np
from PIL import ImageGrab
from PyQt5.QtGui import QGuiApplication


def find_inventory_slots(image_path) -> list[tuple]:
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(
        edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    slot_rects = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 100 < w < 200 and 100 < h < 200 and 0.8 < w / h < 1.2:
            slot_rects.append((x, y, w, h))

    return slot_rects


def save_slot_images(image, slots, prefix="slot"):
    for idx, (x, y, w, h) in enumerate(slots):
        cropped = image[y : y + h, x : x + w]
        filename = f"screenshots/{prefix}_{idx}.png"
        cv2.imwrite(filename, cropped)
        print(f"[INFO] Slot saved: {filename}")


def find_square_slots(image_path, min_size=80, max_size=300, aspect_ratio_tol=0.2):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    gray = cv2.convertScaleAbs(gray, alpha=2.0, beta=-100)
    edges = cv2.Canny(gray, 50, 150)
    kernel = np.ones((3, 3), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    slots = []
    print(len(contours))
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        x, y, w, h = cv2.boundingRect(approx)
        slots.append((x, y, w, h))
        if w >= min_size and w <= max_size and h >= min_size and h <= max_size:
            ratio = w / float(h)
            if (1 - aspect_ratio_tol) <= ratio <= (1 + aspect_ratio_tol):
                slots.append((x, y, w, h))
    slots.sort(key=lambda rect: (rect[0], rect[1]))
    return slots


if __name__ == "__main__":
    path = "inventory_screenshot.png"
    squares = find_square_slots(path)
    print(f"Найдено {len(squares)} предположительно квадратных слотов.")
    for i, (x, y, w, h) in enumerate(squares, 1):
        print(f"{i}: x={x}, y={y}, w={w}, h={h}")


def inventory_scan():
    path = "screenshots/inventory_screenshot.png"
    screen = QGuiApplication.primaryScreen()
    geometry = screen.geometry()
    x = geometry.x()
    y = geometry.y()
    w = geometry.width()
    h = geometry.height()

    bbox = (x, y, x + w, y + h)
    screenshot = ImageGrab.grab(bbox=bbox)
    screenshot.save(path)
    squares = find_square_slots(path)
    print(f"Найдено слотов: {len(squares)}")
    save_slot_images(cv2.imread(path), squares)
