from PIL import ImageGrab, ImageOps, ImageEnhance, Image, ImageFilter
import pytesseract
import os
from dotenv import load_dotenv
import time
from PyQt5.QtGui import QGuiApplication
from app.utils import copy_rename
load_dotenv()

def extract_text_from_area(size: list, image) -> str:
    bbox = (size[0], size[1], size[2], size[3])
    image = image.crop(bbox)
    image = ImageOps.grayscale(image)
    image = ImageEnhance.Contrast(image).enhance(2.5)
    image = ImageOps.invert(image)
    image = image = image.point(lambda x: 0 if x < 140 else 255, "1")
    image = image.resize((image.width * 3, image.height * 3), Image.LANCZOS)
    image = image.filter(ImageFilter.MedianFilter(size=3))
    #if os.getenv("DEBUG", "True") == "True": image.save(f"screenshots/relic_drop_screenshot_{size[0]}.png")
    return pytesseract.image_to_string(
        image,
        lang="eng",
        config='--psm 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "',
    )

def screenshot(type="relics_4", sleep=1):
    if type == "relics_4": filename = f"relic_{time.time()}"
    elif type == "mastery": filename = f"mastery_{time.time()}"
    elif type == "inventory": filename = f"inventory_{time.time()}"
    
    path = f"ml/images/train/{filename}.png"
    example_label = f"ml/labels/example/{type}.txt"

    screen = QGuiApplication.primaryScreen()
    geometry = screen.geometry()
    x = geometry.x()
    y = geometry.y()
    w = geometry.width()
    h = geometry.height()

    if type == "relics_4": time.sleep(sleep)
    bbox = (x, y, x + w, y + h)
    screenshot = ImageGrab.grab(bbox=bbox)
    screenshot.save(path)
    copy_rename(example_label, "ml/labels/train", f"{filename}.txt")
    print(f"[INFO] Screenshot {filename} saved for training")
