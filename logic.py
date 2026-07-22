import storage
from datetime import date

# === Categories & Priorities ===
CATEGORIES = ["Work", "Personal", "Study", "Other"]
PRIORITIES = ["High", "Medium", "Low"]

# === Task Operations ===
def add_task(tasks, text, category="Other", priority="Medium"):
    tasks.append({
        "text": text,
        "done": False,
        "category": category,
        "priority": priority
    })
    storage.save_tasks(tasks)

def toggle_done(tasks, index):
    if 0 <= index < len(tasks):
        tasks[index]["done"] = not tasks[index].get("done", False)
        storage.save_tasks(tasks)

def delete_task(tasks, index):
    if 0 <= index < len(tasks):
        tasks.pop(index)
        storage.save_tasks(tasks)

def edit_task(tasks, index, new_text=None, category=None, priority=None):
    if 0 <= index < len(tasks):
        if new_text is not None:
            tasks[index]["text"] = new_text
        if category in CATEGORIES:
            tasks[index]["category"] = category
        if priority in PRIORITIES:
            tasks[index]["priority"] = priority
        storage.save_tasks(tasks)

def check_new_day_on_start(tasks, last_date_str):
    today = str(date.today())
    if today != last_date_str:
        storage.save_history(last_date_str, tasks)
        tasks.clear()
        storage.save_tasks(tasks)
    return tasks

def convert_old_tasks(tasks):
    """Convert old string tasks or missing keys to structured format"""
    new_tasks = []
    for t in tasks:
        if isinstance(t, str):
            new_tasks.append({
                "text": t,
                "done": False,
                "category": "Other",
                "priority": "Medium"
            })
        elif isinstance(t, dict):
            t.setdefault("text", "Untitled")
            t.setdefault("done", False)
            t.setdefault("category", "Other")
            t.setdefault("priority", "Medium")
            new_tasks.append(t)
    return new_tasks



