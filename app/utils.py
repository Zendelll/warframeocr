import os
import shutil

def copy_rename(original_file, new_folder, new_name):
	shutil.copy(original_file, new_folder)
	new_pathname = f"{new_folder}/{new_name}"
	shutil.move(f"{new_folder}/{original_file.split('/')[-1]}", new_pathname)

def change_last_relic_label(new_label):
    last_relic = [f for f in os.listdir("ml/images/train") if f.endswith(".png")]
    last_relic.sort()
    last_relic = last_relic[-1]
    example_labels = [f for f in os.listdir("ml/labels/example") if f.startswith("relic")]
    if f"{new_label}.txt" in example_labels:
        copy_rename(f"ml/labels/example/{new_label}.txt", "ml/labels/train", f"{".".join(last_relic.split('.')[:2])}.txt")
        print(f"[INFO] Relic {last_relic} labbel chaned to {new_label}")
    else:
        print(f"[ERROR] Label {new_label} not found")
