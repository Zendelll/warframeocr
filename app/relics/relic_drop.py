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
    if word != "":
        result = process.extractOne(word, known_words, scorer=fuzz.token_sort_ratio, score_cutoff=threshold)
        if result:
            print([word, result])
            return result[0]
    return ""


def recognize_items(items_text, cursor) -> list[str]:
    found = []
    for item_text in items_text:
        print(item_text)
        if item_text == "":
            found.append("❌ Nothing found")
            continue
        item = get_item(item_text, cursor)[0]
        text = f"""{item[1]:}
        Price: {item[4]} platinum
        Ducats: {item[3]}"""
        found.append(text)
    if not found:
        print("❌ Nothing found")
        return None
    print("✅ Found:\n" + "\n".join(found))
    return found

def recognize_item(item_name, cursor) -> list[str]:
    if item_name != "":
        item = get_item(item_name, cursor)[0]
        if item:
            text = f"""{item[1]}:
    Price: {item[4]} platinum
    Ducats: {item[3]}"""
            print(f"✅ Found: {item[1]} Price: {item[4]} Ducats: {item[3]}")
            return text
    print("❌ Nothing found")
    return "❌ Nothing found"

def main_logic(overlay_relic_queue: Queue):
    geometry = QGuiApplication.primaryScreen().geometry()
    screenshot = ImageGrab.grab(bbox=(geometry.x(), geometry.y(), geometry.x() + geometry.width(), geometry.y() + geometry.height()))
    results = model.predict(source=screenshot, conf=0.8)
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        known_words = [item[0] for item in get_all_item_names(cursor)]
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
                item_text = recognize_item(item_name, cursor)
                windows.append(((size["x1"], size["y2"]+100, size["x2"]-size["x1"], 200), item_text))
        overlay_relic_queue.put(windows)
    print("[Info] Added windows to queue")
