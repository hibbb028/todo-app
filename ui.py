import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import date, datetime
from PIL import Image, ImageTk
import config, storage, logic

def run_app():
    global root, entry, listbox, tasks, date_label
    global _bg_img_original, _bg_img_display, bg_label
    global last_date_str
    global drag_data

    drag_data = {"index": None}

    # === Load Tasks ===
    tasks, last_date_str = storage.load_tasks()
    tasks = logic.check_new_day_on_start(tasks, last_date_str)

    # === Root Window ===
    root = tk.Tk()
    root.title(config.TITLE)
    root.geometry(f"{config.WINDOW_W}x{config.WINDOW_H}")
    root.minsize(420, 560)

    # === Background ===
    _bg_img_original = None
    _bg_img_display = None
    bg_label = tk.Label(root)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def safe_load_bg():
        global _bg_img_original
        if config.BG_PATH and config.os.path.exists(config.BG_PATH):
            _bg_img_original = Image.open(config.BG_PATH)
            return True
        return False

    def resize_bg(event=None):
        global _bg_img_display
        if _bg_img_original is None:
            return
        w, h = root.winfo_width(), root.winfo_height()
        img = _bg_img_original.copy()
        img_ratio = img.width / img.height
        win_ratio = w / h
        if win_ratio > img_ratio:
            new_w, new_h = w, int(w / img_ratio)
        else:
            new_h, new_w = h, int(h * img_ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left, top = (new_w - w) // 2, (new_h - h) // 2
        img = img.crop((left, top, left + w, top + h))
        _bg_img_display = ImageTk.PhotoImage(img)
        bg_label.config(image=_bg_img_display)

    if safe_load_bg():
        resize_bg()
    root.bind("<Configure>", resize_bg)

    # === Task Functions ===
    def update_listbox():
        listbox.delete(0, tk.END)
        keyword = search_var.get().lower()
        for i, task in enumerate(tasks, 1):
            if keyword and keyword not in task["text"].lower():
                continue
            if filter_category_var.get() != "All" and task["category"] != filter_category_var.get():
                continue
            if filter_priority_var.get() != "All" and task["priority"] != filter_priority_var.get():
                continue
            if filter_date_var.get() != "All" and task["date"] != filter_date_var.get():
                continue
            mark = "🌸" if task.get("done") else ""
            due_text = f" (Due: {task.get('due','N/A')})" if task.get("due") else ""
            text = f"{i}. {task['text']} [{task['category']}] ({task['priority']}){due_text} {mark}"
            listbox.insert(tk.END, text)
            color = "gray" if task.get("done") else (
                "red" if task["priority"]=="High" else
                "orange" if task["priority"]=="Medium" else "green"
            )
            listbox.itemconfig(tk.END, {'fg': color})

    def add_task_ui():
        text = entry.get().strip()
        if not text:
            return messagebox.showwarning("⚠️ Warning", "Task cannot be empty!")
        due_date = simpledialog.askstring("⏰ Due Date (Optional)", "Enter due date (YYYY-MM-DD HH:MM):", parent=root)
        task_data = {
            "text": text,
            "done": False,
            "category": category_var.get(),
            "priority": priority_var.get(),
            "date": str(date.today()),
            "due": due_date
        }
        tasks.append(task_data)
        storage.save_tasks(tasks)
        entry.delete(0, tk.END)
        update_listbox()
        update_date_options()

    def mark_done_ui():
        sel = listbox.curselection()
        if not sel: return messagebox.showwarning("⚠️ Warning", "Select a task to mark done.")
        logic.toggle_done(tasks, sel[0])
        update_listbox()

    def delete_task_ui():
        sel = listbox.curselection()
        if not sel: return messagebox.showwarning("⚠️ Warning", "Select a task to delete.")
        logic.delete_task(tasks, sel[0])
        update_listbox()
        update_date_options()

    def edit_task_ui():
        sel = listbox.curselection()
        if not sel: return messagebox.showwarning("⚠️ Warning", "Select a task to edit.")
        index = sel[0]
        task = tasks[index]
        new_text = simpledialog.askstring("✏️ Edit Task", "Update task:", initialvalue=task["text"])
        if not new_text or not new_text.strip(): return
        edit_window = tk.Toplevel(root)
        edit_window.title("Edit Task")
        tk.Label(edit_window, text="Category:").pack(pady=2)
        cat_var = tk.StringVar(value=task.get("category","Other"))
        tk.OptionMenu(edit_window, cat_var, *logic.CATEGORIES).pack(pady=2)
        tk.Label(edit_window, text="Priority:").pack(pady=2)
        pri_var = tk.StringVar(value=task.get("priority","Medium"))
        tk.OptionMenu(edit_window, pri_var, *logic.PRIORITIES).pack(pady=2)
        due_var = tk.StringVar(value=task.get("due",""))
        tk.Label(edit_window, text="Due Date (YYYY-MM-DD HH:MM)").pack(pady=2)
        tk.Entry(edit_window, textvariable=due_var).pack(pady=2)
        def save_changes():
            logic.edit_task(tasks, index, new_text.strip(), cat_var.get(), pri_var.get())
            tasks[index]["due"] = due_var.get()
            storage.save_tasks(tasks)
            update_listbox()
            edit_window.destroy()
        tk.Button(edit_window, text="Save", bg="#FFB6C1", command=save_changes).pack(pady=5)

    # === Drag-and-Drop Functions ===
    def start_drag(event):
        drag_data["index"] = listbox.nearest(event.y)

    def do_drag(event):
        pass

    def stop_drag(event):
        new_index = listbox.nearest(event.y)
        old_index = drag_data["index"]
        if old_index is not None and new_index != old_index:
            task = tasks.pop(old_index)
            tasks.insert(new_index, task)
            storage.save_tasks(tasks)
            update_listbox()
        drag_data["index"] = None

    # === Search & Filters ===
    search_var = tk.StringVar()
    filter_category_var = tk.StringVar(value="All")
    filter_priority_var = tk.StringVar(value="All")
    filter_date_var = tk.StringVar(value="All")
    search_var.trace_add("write", lambda *args: update_listbox())
    filter_category_var.trace_add("write", lambda *args: update_listbox())
    filter_priority_var.trace_add("write", lambda *args: update_listbox())
    filter_date_var.trace_add("write", lambda *args: update_listbox())

    # === Sidebar Buttons with Smooth Hover ===
    sidebar = tk.Frame(root, bg="#FFD6E0")
    sidebar.place(relx=0, rely=0, relwidth=0.25, relheight=1)
    btn_style = dict(font=("Comic Sans MS",12,"bold"), bg="#FFB6C1", fg="black",
                     activebackground="#FF69B4", relief="raised", bd=3, width=14, pady=6)
    buttons = [
        ("➕ Add Task", add_task_ui),
        ("✅ Mark Done", mark_done_ui),
        ("❌ Delete Task", delete_task_ui),
        ("✏️ Edit Task", edit_task_ui),
        ("📊 Show Progress", lambda: show_piechart())
    ]
    sidebar_buttons = []
    def smooth_hover(widget, start="#FFB6C1", end="#FF69B4", steps=10, delay=20):
        def on_enter(e):
            step = 0
            def fade():
                nonlocal step
                if step <= steps:
                    widget.config(bg=_blend_color(start,end,step/steps))
                    step += 1
                    widget.after(delay, fade)
            fade()
        def on_leave(e):
            step = 0
            def fade():
                nonlocal step
                if step <= steps:
                    widget.config(bg=_blend_color(end,start,step/steps))
                    step += 1
                    widget.after(delay, fade)
            fade()
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    def _blend_color(c1,c2,t):
        """Blend two hex colors"""
        c1 = c1.lstrip("#")
        c2 = c2.lstrip("#")
        r1,g1,b1 = int(c1[:2],16),int(c1[2:4],16),int(c1[4:],16)
        r2,g2,b2 = int(c2[:2],16),int(c2[2:4],16),int(c2[4:],16)
        r = int(r1+(r2-r1)*t)
        g = int(g1+(g2-g1)*t)
        b = int(b1+(b2-b1)*t)
        return f"#{r:02x}{g:02x}{b:02x}"
    for text, cmd in buttons:
        btn = tk.Button(sidebar, text=text, command=cmd, **btn_style)
        btn.pack(pady=14)
        smooth_hover(btn)
        sidebar_buttons.append(btn)

    # === Main Frame ===
    main_frame = tk.Frame(root, bg="#FFF0F5")
    main_frame.place(relx=0.25, rely=0, relwidth=0.75, relheight=1)
    title_label = tk.Label(main_frame, text=config.TITLE, font=("Comic Sans MS",20,"bold"),
                           bg="#FFF0F5", fg="#D81B60", pady=6)
    title_label.pack(fill="x")
    date_label = tk.Label(main_frame, text=date.today().strftime("%A, %B %d, %Y"),
                          font=("Comic Sans MS",12), bg="#FFF0F5", fg="#4A148C", pady=4)
    date_label.pack(fill="x")

    # === Controls Frame ===
    controls = tk.Frame(main_frame, bg="#FFE4E8")
    controls.pack(fill="x", padx=5, pady=5)
    entry = tk.Entry(controls, width=25, font=("Comic Sans MS",14),
                     bg="#FFF8FB", fg="#6A0572", relief="groove", bd=3)
    entry.grid(row=0,column=0,padx=4,pady=6)
    category_var = tk.StringVar(value=logic.CATEGORIES[0])
    priority_var = tk.StringVar(value=logic.PRIORITIES[1])
    tk.OptionMenu(controls, category_var,*logic.CATEGORIES).grid(row=0,column=1,padx=2)
    tk.OptionMenu(controls, priority_var,*logic.PRIORITIES).grid(row=0,column=2,padx=2)
    search_frame = tk.Frame(controls,bg="#FFE4E8")
    search_frame.grid(row=1,column=0,columnspan=3,sticky="ew",pady=4)
    tk.Label(search_frame,text="🔍",bg="#FFF8FB").pack(side="left",padx=4)
    tk.Entry(search_frame,textvariable=search_var,font=("Comic Sans MS",12),
             bg="#FFF8FB", fg="#6A0572", relief="groove", bd=2).pack(side="left",fill="x",expand=True)
    tk.OptionMenu(controls, filter_category_var,"All",*logic.CATEGORIES).grid(row=1,column=3,padx=2)
    tk.OptionMenu(controls, filter_priority_var,"All",*logic.PRIORITIES).grid(row=1,column=4,padx=2)
    def update_date_options():
        dates = ["All"] + sorted({t.get("date") for t in tasks})
        menu = controls.grid_slaves(row=1,column=5)
        if menu: menu[0].destroy()
        tk.OptionMenu(controls, filter_date_var,*dates).grid(row=1,column=5,padx=2)
    update_date_options()

    # === Task List ===
    list_frame = tk.Frame(main_frame,bg="#FFF0F5")
    list_frame.pack(fill="both",expand=True,padx=5,pady=5)
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right",fill="y")
    listbox = tk.Listbox(list_frame,width=40,font=("Segoe Script",12),
                         bg="#FFF8FB", fg="#4A148C", selectbackground="#F8BBD0",
                         highlightthickness=0, yscrollcommand=scrollbar.set)
    listbox.pack(side="left",fill="both",expand=True)
    scrollbar.config(command=listbox.yview)
    listbox.bind("<Button-1>", start_drag)
    listbox.bind("<B1-Motion>", do_drag)
    listbox.bind("<ButtonRelease-1>", stop_drag)

    # === Pie Chart ===
    def show_piechart():
        import matplotlib.pyplot as plt
        done_count = sum(1 for t in tasks if t.get("done"))
        pending_count = len(tasks)-done_count
        if not tasks:
            messagebox.showinfo("Info","No tasks to show.")
            return
        fig, ax = plt.subplots()
        ax.pie([done_count,pending_count],labels=["Done","Pending"],colors=["#4CAF50","#FF5722"],autopct='%1.1f%%')
        ax.set_title("Task Completion")
        plt.show()

    # === Reminder Check ===
    def check_reminders():
        now = datetime.now()
        for t in tasks:
            if t.get("due") and not t.get("done"):
                try:
                    due_dt = datetime.strptime(t["due"],"%Y-%m-%d %H:%M")
                    if due_dt <= now and not t.get("notified"):
                        messagebox.showinfo("⏰ Reminder",f"Task Due: {t['text']}")
                        t["notified"] = True
                except:
                    continue
        root.after(60_000,check_reminders)

    # === New Day Check ===
    def periodic_check():
        global tasks,last_date_str
        today = str(date.today())
        if today != last_date_str:
            storage.save_history(last_date_str,tasks)
            tasks.clear()
            storage.save_tasks(tasks)
            last_date_str = today
            date_label.config(text=date.today().strftime("%A, %B %d, %Y"))
            update_listbox()
            update_date_options()
        root.after(60_000,periodic_check)

    # === Initial Load ===
    update_listbox()
    periodic_check()
    check_reminders()
    print("✅ Daily Flow – Full UI polished with smooth hover, drag-drop, reminders")
    root.mainloop()








































