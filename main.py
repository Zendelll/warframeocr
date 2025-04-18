import sys
import threading
from threading import Event
from pynput import keyboard
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from queue import Queue
from traceback import print_exc

from app.db import init
from app.update_db import update_db
from app.inventory_scan import inventory_scan
from app.relics.log_listener import watch_ee_log
from app.relics.qt import process_overlay_queue

app = QApplication([])
stop_event = Event()
overlay_relic_queue = Queue()

def on_press(key):
    try:
        if key == keyboard.Key.page_up:
            print("[INFO] Page Up pressed — scanning inventory...")
            threading.Thread(target=inventory_scan).start()
        elif key == keyboard.Key.home:
            print("[INFO] Home pressed — updating db...")
            threading.Thread(target=update_db).start()
        elif key == keyboard.Key.page_down:
            print("[INFO] Page Down pressed — exiting...")
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
    init()
    queue_timer = QTimer()
    queue_timer.timeout.connect(lambda: process_overlay_queue(overlay_relic_queue))
    queue_timer.start(50)
    threading.Thread(target=start_key_listener).start()
    threading.Thread(target=lambda: watch_ee_log(stop_event, overlay_relic_queue)).start()
    sys.exit(app.exec_())
