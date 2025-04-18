from PIL import ImageGrab, ImageOps, ImageEnhance, Image, ImageFilter
import pytesseract
import os
from dotenv import load_dotenv
import time
from PyQt5.QtGui import QGuiApplication
load_dotenv()

def extract_text_from_area(size: dict) -> str:
    bbox = (size["x"], size["y"], size["x"] + size["width"], size["y"] + size["height"])
    image = ImageGrab.grab(bbox)
    image = ImageOps.grayscale(image)
    image = ImageEnhance.Contrast(image).enhance(2.5)
    image = ImageOps.invert(image)
    image = image = image.point(lambda x: 0 if x < 140 else 255, "1")
    image = image.resize((image.width * 3, image.height * 3), Image.LANCZOS)
    image = image.filter(ImageFilter.MedianFilter(size=3))
    if os.getenv("DEBUG", "True") == "True": image.save(f"screenshots/relic_drop_screenshot_{size["x"]}.png")
    return pytesseract.image_to_string(
        image,
        lang="eng",
        config='--psm 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "',
    )

def screenshot(sleep=1):
    path = f"ml/images/train/relic_{time.time()}.png"
    screen = QGuiApplication.primaryScreen()
    geometry = screen.geometry()
    x = geometry.x()
    y = geometry.y()
    w = geometry.width()
    h = geometry.height()

    time.sleep(sleep)
    bbox = (x, y, x + w, y + h)
    screenshot = ImageGrab.grab(bbox=bbox)
    screenshot.save(path)