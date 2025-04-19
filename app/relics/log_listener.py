import time
import os
from dotenv import load_dotenv
from collections import deque
from app.relics.ocr import screenshot
import threading
from app.relics.relic_drop import main_logic
from traceback import print_exc

load_dotenv()
EE_LOG_PATH = os.getenv("EE_LOG_PATH", "")
KEY_PHRASE = "ProjectionRewardChoice.lua: Relic rewards initialized"
last_trigger_time = 0

def tail_lines(file_path, num_lines=20):
    with open(file_path, "rb") as f:
        f.seek(0, os.SEEK_END)
        buffer = bytearray()
        pointer = f.tell()
        while pointer >= 0:
            f.seek(pointer)
            read_byte = f.read(1)
            if read_byte == b"\n":
                num_lines -= 1
                if num_lines == 0:
                    break
            buffer.extend(read_byte)
            pointer -= 1
        return deque(buffer[::-1].decode(errors="ignore").splitlines(), maxlen=2000)

def watch_ee_log(stop_event, overlay_relic_queue):
    global last_trigger_time
    print("[INFO] Starting EE.log watcher")

    while not stop_event.is_set():
        try:
            if not os.path.exists(EE_LOG_PATH):
                print("[WARNING] EE.log not found")
                time.sleep(1)
                continue

            recent_lines = tail_lines(EE_LOG_PATH, num_lines=100)
            for line in recent_lines:
                if KEY_PHRASE in line:
                    trigger_time = line.split()[0]
                    if trigger_time != last_trigger_time:
                        print("[INFO] Relic rewards initialized")
                        last_trigger_time = trigger_time
                        #screenshot()
                        time.sleep(0.5)
                        threading.Thread(
                            target= lambda: main_logic(overlay_relic_queue)
                        ).start()
                        print("[INFO] Relic rewards logic stated")
        except Exception as e:
            print(f"[ERROR] {e}")
            print_exc()
        time.sleep(0.5)