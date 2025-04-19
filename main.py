import sys
import os
import dotenv
import threading
from pynput import keyboard
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from queue import Queue
from traceback import print_exc

from app.db import init, update_db, close_memory
from app.relics.log_listener import watch_ee_log
from app.relics.qt import process_overlay_queue
#from app.utils import change_last_relic_label
#from app.relics.ocr import screenshot
from app.relics.relic_drop import main_logic

app = QApplication([])
stop_event = threading.Event()
overlay_relic_queue = Queue()

def on_press(key):
    try:
        if key == keyboard.Key.page_up:
            print("[INFO] Page Up pressed — Starting manual relic logic...")
            threading.Thread(target=lambda: main_logic(overlay_relic_queue)).start()
        #elif key == keyboard.Key.page_down:
        #    print("[INFO] Page Down pressed — Changing last relic to 2...")
        #    threading.Thread(target=lambda: change_last_relic_label("relics_2")).start()
        elif key == keyboard.Key.home:
            print("[INFO] Home pressed — updating db...")
            threading.Thread(target=update_db).start()
        #elif key == keyboard.Key.insert:
        #    print("[INFO] Insert pressed — screenshoting inventorty...")
        #    threading.Thread(target=lambda: screenshot("inventory")).start()
        #elif key == keyboard.Key.delete:
        #    print("[INFO] Delete pressed — screenshoting mastery...")
        #    threading.Thread(target=lambda: screenshot("mastery")).start()
        elif key == keyboard.Key.end:
            print("[INFO] End pressed — exiting...")
            stop_event.set()
            app.quit()
            return False  # останавливает listener
    except Exception as e:
        print(f"[ERROR] {e}")
        print_exc()


def start_key_listener():
    print("[INFO] Starting key listener")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    print("[INFO] Starting app")
    init()
    queue_timer = QTimer()
    queue_timer.timeout.connect(lambda: process_overlay_queue(overlay_relic_queue))
    queue_timer.start(50)
    threading.Thread(target=start_key_listener).start()
    threading.Thread(target=lambda: watch_ee_log(stop_event, overlay_relic_queue)).start()
    sys.exit(app.exec_())
    close_memory()
