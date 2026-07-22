import os

# === Window Settings ===
WINDOW_W, WINDOW_H = 520, 680
TITLE = "🌸 Daily Flow 🌸"

# === File Paths ===
BASE_DIR = os.path.dirname(__file__)
BG_PATH = os.path.join(BASE_DIR, "bg.jpg")
TASKS_FILE = os.path.join(BASE_DIR, "tasks.json")
HISTORY_FILE = os.path.join(BASE_DIR, "history.txt")
