import re
import sqlite3
import json
import os
from dotenv import load_dotenv 
from app.relics.ocr import extract_text_from_area
from app.db import get_all_item_names, get_item
from rapidfuzz import process, fuzz
from queue import Queue
from ultralytics import YOLO
from PyQt5.QtGui import QGuiApplication
from PIL import ImageGrab

load_dotenv()
DB_NAME = os.getenv("DB_NAME", "items.db")
model = YOLO(os.getenv("MODEL_PATH", "ml/best.pt"))


def correct_word(word, known_words, threshold=60):
    word = re.search(r"[A-Z][a-z]+.*", word).group(0)
    if word != "":
        result = process.extractOne(word, known_words, scorer=fuzz.token_sort_ratio, score_cutoff=threshold)
        if result:
            print([word, result])
            return result[0]
    return ""

def recognize_item(item_name) -> list[str]:
    if item_name != "":
        item = get_item(item_name)
        if item:
            text = f"""{item.name}:
    Ducats: {item.ducats}
    Item: {item.price}p sold {item.sold}
    Set: {item.item_set_price}p sold {item.item_set_sold}
    Vaulted: {item.vaulted}
    Items to craft: {item.items_to_craft}"""
            print(f"✅ Found: {item.name} {item.price}p sold {item.sold}")
            return text
    print("❌ Nothing found")
    return "❌ Nothing found"

def main_logic(overlay_relic_queue: Queue):
    geometry = QGuiApplication.primaryScreen().geometry()
    screenshot = ImageGrab.grab(bbox=(geometry.x(), geometry.y(), geometry.x() + geometry.width(), geometry.y() + geometry.height()))
    results = model.predict(source=screenshot, conf=0.8)
    known_words = [item[0] for item in get_all_item_names()]
    windows = []
    for box in results[0].boxes:
        if box.conf.item() >= 0.8:
            size = {}
            sizes = box.xyxy[0].tolist()
            size["x1"] = round(sizes[0])
            size["y1"] = round(sizes[1])
            size["x2"] = round(sizes[2])
            size["y2"] = round(sizes[3])
            item_name = correct_word(
                re.sub(
                    r"(?<=[a-z])(?=[A-Z])",
                    " ",
                    " ".join(extract_text_from_area([size["x1"], size["y2"]-50, size["x2"], size["y2"]], screenshot).split()),
                ),
                known_words,
            )
            item_text = recognize_item(item_name)
            windows.append(((size["x1"], size["y2"]+100, size["x2"]-size["x1"], 200), item_text))
    overlay_relic_queue.put(windows)
    print("[Info] Added windows to queue")
