import json, os
from datetime import date
import config
from logic import convert_old_tasks

def load_tasks():
    """Load tasks and last_date from tasks.json, convert old tasks if needed"""
    if os.path.exists(config.TASKS_FILE):
        with open(config.TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        tasks = data.get("tasks", [])
        tasks = convert_old_tasks(tasks)  # ensure all tasks have new structure
        last_date = data.get("last_date", str(date.today()))
        return tasks, last_date
    return [], str(date.today())

def save_tasks(tasks):
    """Save tasks with today's date into tasks.json"""
    data = {"last_date": str(date.today()), "tasks": tasks}
    with open(config.TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_history(last_date, tasks):
    """Append finished day's tasks to history.txt"""
    if not tasks:
        return
    with open(config.HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"--- {last_date} ---\n")
        for i, t in enumerate(tasks, 1):
            status = "✔" if t.get("done", False) else "❌"
            category = t.get("category", "Other")
            priority = t.get("priority", "Medium")
            f.write(f"{i}. {t['text']} [{category}] [{priority}] [{status}]\n")
        f.write("\n")


