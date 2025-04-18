import re
import sqlite3
import json
import os
from dotenv import load_dotenv 
from app.relics.ocr import extract_text_from_area
from app.db import get_all_item_names, get_item
from fuzzywuzzy import process, fuzz
from queue import Queue

load_dotenv()
RELIC_SIZE = json.loads(os.getenv("RELIC_SIZE", '{"x": 477,"y": 410,"width": 239,"height": 50,"space": 4}'))
DB_NAME = os.getenv("DB_NAME", "items.db")


def correct_word(word, known_words, threshold=70):
    if word == "":
        return ""
    result = process.extractBests(word, known_words, scorer=fuzz.token_sort_ratio)
    print([word, result])
    return result[0][0]


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


def main_logic(overlay_relic_queue: Queue):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        known_words = [item[0] for item in get_all_item_names(cursor)]
        items_text = []
        for i in range(4):
            size = RELIC_SIZE.copy()
            size["x"] += (size["width"] + size["space"]) * i
            items_text.append(
                correct_word(
                    re.sub(
                        r"(?<=[a-z])(?=[A-Z])",
                        " ",
                        " ".join(extract_text_from_area(size).split()),
                    ),
                    known_words,
                )
            )
        print(items_text)
        items = recognize_items(items_text, cursor)
        if not items:
            return
        windows = []
        for index, item in enumerate(items):
            size = RELIC_SIZE.copy()
            size["x"] += (size["width"] + size["space"]) * index
            windows.append((size, item))
        overlay_relic_queue.put(windows)
    print("[Info] Added windows to queue")
