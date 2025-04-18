from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


def create_overlay_window(size: dict, text: dict) -> QWidget:
    window = QWidget()
    window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
    window.setAttribute(Qt.WA_TranslucentBackground)

    label = QLabel(text)
    label.setFont(QFont("Helvetica", 12))
    label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    label.setStyleSheet(
        "color: white; background-color: rgba(0, 0, 0, 160); padding: 5px;"
    )
    label.setWordWrap(True)

    layout = QVBoxLayout()
    layout.addWidget(label)
    layout.setContentsMargins(10, 10, 10, 10)
    window.setLayout(layout)

    window.setGeometry(size["x"] - 7, 600, 235, 200)
    return window

def process_overlay_queue(overlay_relic_queue):
    while not overlay_relic_queue.empty():
        windows_sizes = overlay_relic_queue.get()
        windows = []
        for window in windows_sizes:
            window = create_overlay_window(window[0], window[1])
            window.show()
            windows.append(window)
        QTimer.singleShot(15000, lambda: [w.close() for w in windows])