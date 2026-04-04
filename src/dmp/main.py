import json
import os
import time
import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

import datetime
from threading import Timer
from tkinter import filedialog

APP_NAME = "dmp"

config = []

# Material-inspired color palette
COLORS = {
    "bg": "#2E2E2E",
    "surface": "#3C3C3C",
    "primary": "#6200EE",
    "primary_dark": "#3700B3",
    "secondary": "#03DAC6",
    "error": "#CF6679",
    "on_bg": "#E0E0E0",
    "on_surface": "#FFFFFF",
    "on_primary": "#FFFFFF",
    "muted": "#9E9E9E",
    "entry_bg": "#4A4A4A",
    "start": "#4CAF50",
    "start_active": "#388E3C",
    "stop": "#F44336",
    "stop_active": "#D32F2F",
}
FONT = "Segoe UI" if sys.platform == "win32" else "Helvetica"


def apply_theme(root):
    root.configure(bg=COLORS["bg"])
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=COLORS["bg"], foreground=COLORS["on_bg"],
                     font=(FONT, 10))
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Card.TFrame", background=COLORS["surface"])
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["on_bg"],
                     font=(FONT, 10))
    style.configure("Card.TLabel", background=COLORS["surface"])
    style.configure("Bold.TLabel", font=(FONT, 10, "bold"))
    style.configure("Bold.Card.TLabel", background=COLORS["surface"], font=(FONT, 10, "bold"))
    style.configure("Timer.TLabel", font=(FONT, 22, "bold"), foreground=COLORS["secondary"])
    style.configure("Muted.TLabel", foreground=COLORS["muted"], font=(FONT, 9))

    style.configure("TButton", background=COLORS["primary"], foreground=COLORS["on_primary"],
                     font=(FONT, 10), padding=(12, 6), borderwidth=0)
    style.map("TButton",
              background=[("active", COLORS["primary_dark"]), ("pressed", COLORS["primary_dark"])],
              relief=[("pressed", "flat"), ("!pressed", "flat")])

    style.configure("Icon.TButton", background=COLORS["surface"], foreground=COLORS["muted"],
                     padding=(4, 2), font=(FONT, 12), width=2)
    style.map("Icon.TButton",
              background=[("active", COLORS["primary"])],
              foreground=[("active", COLORS["on_primary"])])

    style.configure("Delete.TButton", background=COLORS["surface"], foreground=COLORS["error"],
                     padding=(4, 2), font=(FONT, 12), width=2)
    style.map("Delete.TButton",
              background=[("active", COLORS["error"])],
              foreground=[("active", COLORS["on_primary"])])

    style.configure("TEntry", fieldbackground=COLORS["entry_bg"], foreground=COLORS["on_surface"],
                     insertcolor=COLORS["on_surface"], borderwidth=1, padding=4)
    style.map("TEntry", fieldbackground=[("focus", "#555555")])

    style.configure("Vertical.TScrollbar", background=COLORS["surface"],
                     troughcolor=COLORS["bg"], borderwidth=0, arrowsize=0)


class Run:
    def __init__(self, save_dir: Path, start_time: datetime.datetime = None):
        self.events = []
        self.start_time = start_time
        self.save_dir = save_dir

    def save_as(self, path: Path):
        old = self.save()
        os.rename(old, path)

    def save(self) -> Path:
        path = self.save_dir / self.start_time.strftime("%Y_%m_%d_%H_%M_%S.csv")
        with open(path, "w+") as f:
            f.write(f"{self.start_time}, {'Start'}\n")
            for m, d in self.events:
                f.write(f"{d}, {m}\n")
            f.write(f"{datetime.datetime.now()}, {'Stop'}\n")
        return path


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def get_datadir() -> Path:

    """
    Returns the platform-specific directory for persistent application data.

    - Windows: %APPDATA%/<app> (fallback: ~/AppData/Roaming)
    - Linux: $XDG_DATA_HOME/<app> (fallback: ~/.local/share)
    - macOS: ~/Library/Application Support/<app>
    """

    home = Path.home()

    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", home / "AppData/Roaming")) / APP_NAME
    elif sys.platform == "linux":
        return Path(os.environ.get("XDG_DATA_HOME", home / ".local/share")) / APP_NAME
    elif sys.platform == "darwin":
        return home / "Library/Application Support" / APP_NAME
    else:
        raise Exception(f"Unsupported platform: {sys.platform}")


config_path = (get_datadir() / ".config").absolute()
if not os.path.exists(get_datadir().absolute()):
    os.mkdir(get_datadir().absolute())


def load_config() -> dict:
    if not os.path.exists(config_path):
        return {"keys": [("", "", "")] * 3, "save_dir": ""}
    with open(config_path, "r") as f:
        data = json.loads(f.read())
    # migrate old list format
    if isinstance(data, list):
        return {"keys": data, "save_dir": ""}
    return data


def write_config(cfg: dict):
    with open(config_path, "w+") as f:
        f.write(json.dumps(cfg))


class KeyBoardListener:

    def __init__(self, frame=None):
        self.bt_down = {}
        self.bt_up = {}
        self._click_listeners = []
        self._long_listeners = []
        if frame:
            frame.bind("<KeyPress>", self._on_key_down)
            frame.bind("<KeyRelease>", self._on_key_up)

    def on_click(self, callback):
        self._click_listeners.append(callback)

    def on_long_click(self, callback):
        self._long_listeners.append(callback)

    def _on_key_down(self, e):
        if e.keysym not in self.bt_down:
            self.bt_down[e.keysym] = time.time()

    def _on_key_up(self, e):
        if e.keysym in self.bt_down:
            start = self.bt_down[e.keysym]
            delta = time.time() - start
            if delta < 0.2:
                for cb in self._click_listeners:
                    cb(e.keysym)
            else:
                for cb in self._long_listeners:
                    cb(e.keysym)
            del self.bt_down[e.keysym]


def save_config(entry_guis: list):
    keys = []
    for key, short, long in entry_guis:
        if key.get():
            keys.append((key.get(), short.get(), long.get()))
    cfg = load_config()
    cfg["keys"] = keys
    write_config(cfg)


def add_entry_row(frame, row, entry_guis: list, key_text="", short_text="", long_text=""):

    e1 = ttk.Entry(frame, width=3)
    e1.insert(0, key_text)
    e1.grid(row=row, column=0, padx=(8, 4), pady=3, sticky="ew")

    e2 = ttk.Entry(frame)
    e2.grid(row=row, column=1, padx=4, pady=3, sticky="ew")
    e2.insert(0, short_text)

    e3 = ttk.Entry(frame)
    e3.grid(row=row, column=2, padx=4, pady=3, sticky="ew")
    e3.insert(0, long_text)

    def remove():
        entry_guis.remove((e1, e2, e3))
        e1.grid_remove()
        e2.grid_remove()
        e3.grid_remove()
        del_btn.grid_remove()
        save_config(entry_guis)

    del_btn = ttk.Button(frame, text="x", style="Delete.TButton", command=remove)
    del_btn.grid(row=row, column=3, padx=(4, 8), pady=3)

    e1.bind("<KeyRelease>", lambda _: save_config(entry_guis))
    e2.bind("<KeyRelease>", lambda _: save_config(entry_guis))
    e3.bind("<KeyRelease>", lambda _: save_config(entry_guis))

    entry_guis.append((e1, e2, e3))


def update_time(string_var, start):
    delta = datetime.datetime.now() - start
    string_var.set(str(datetime.timedelta(seconds=int(delta.total_seconds()))))


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DMP")
        self.root.geometry("520x540")
        self.root.minsize(480, 400)
        apply_theme(self.root)

        self.t = None
        self.s = None
        self.timer: Timer | None = None
        self.run = None

        self.cancel_btn = None
        self.save_btn = None
        self.start_btn = None

        self.entry_guis = []
        self.short_mapping = {}
        self.long_mapping = {}

        self.path_info_var = tk.StringVar()
        self.time_info_var = tk.StringVar()
        self.save_dir_var = tk.StringVar()

        cfg = load_config()
        self.save_dir_var.set(cfg.get("save_dir", ""))

        if not self.save_dir_var.get():
            self._prompt_save_dir()

        self.keyboard = KeyBoardListener(self.root)
        self.keyboard.on_click(self.on_key_click)
        self.keyboard.on_long_click(self.on_key_long_click)

        self.dir_frame = self.create_dir_picker()
        self.top_frame = self.create_top()
        self.mid_frame = self.create_middle()
        self.bot_frame = self.create_bottom()

    def runloop(self):
        self.root.mainloop()

    def _prompt_save_dir(self):
        directory = filedialog.askdirectory(title="Choose directory for saving recordings")
        if directory:
            self.save_dir_var.set(directory)
            cfg = load_config()
            cfg["save_dir"] = directory
            write_config(cfg)

    def _change_save_dir(self):
        self._prompt_save_dir()

    def create_dir_picker(self):
        frame = ttk.Frame(self.root, style="Card.TFrame")

        ttk.Label(frame, text="Autosave directory:", style="Bold.Card.TLabel").pack(side="left", padx=(10, 5))
        ttk.Label(frame, textvariable=self.save_dir_var, style="Card.TLabel").pack(side="left", fill="x", expand=True)
        ttk.Button(frame, text="Change", command=self._change_save_dir).pack(side="right", padx=10, pady=6)

        frame.pack(fill="x", padx=10, pady=(10, 0))
        return frame

    def create_top(self):
        cfg = load_config()
        data = cfg["keys"]

        frame = ttk.Frame(self.root, style="Card.TFrame")
        frame.columnconfigure(0, weight=0, minsize=50)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=0)

        ttk.Label(frame, text="Key", style="Bold.Card.TLabel").grid(row=0, column=0, padx=(8, 4), pady=(8, 2))
        ttk.Label(frame, text="Short press", style="Bold.Card.TLabel").grid(row=0, column=1, padx=4, pady=(8, 2))
        ttk.Label(frame, text="Long press", style="Bold.Card.TLabel").grid(row=0, column=2, padx=4, pady=(8, 2))
        self.entry_guis.clear()
        for idx, (key, short, long) in enumerate(data):
            add_entry_row(frame, idx + 1, self.entry_guis, key, short, long)

        add = ttk.Button(frame, text="+", style="Icon.TButton",
                         command=lambda: add_entry_row(frame, len(self.entry_guis) + 1, self.entry_guis))
        add.grid(row=0, column=3, padx=(4, 8), pady=(5, 2))

        frame.pack(fill="x", padx=10, pady=(10, 5))
        return frame

    def create_middle(self):
        frame = ttk.Frame(self.root, style="Card.TFrame")
        self.t = tk.Text(frame, height=15, bg=COLORS["entry_bg"], fg=COLORS["on_surface"],
                         insertbackground=COLORS["on_surface"], selectbackground=COLORS["primary"],
                         font=(FONT, 10), relief="flat", padx=8, pady=8, borderwidth=0)
        self.s = ttk.Scrollbar(frame, command=self.t.yview)
        self.t.config(yscrollcommand=self.s.set)
        self.s.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 2), pady=2)
        self.t.pack(side=tk.LEFT, fill="both", expand=True, padx=(2, 0), pady=2)
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        return frame

    def save_file(self):
        path = filedialog.asksaveasfilename()
        if path:
            self.run.save_as(path)
            self.path_info_var.set(f"Saved to: {str(path)}")

    def record_event(self, x, mapping):
        if x in mapping:
            m = mapping[x]
            d = datetime.datetime.now()
            self.run.events.append((m, d))
            self.t.insert("1.0", f"{d}: {m}\n")
            self.run.save()

    def on_start(self):
        if not self.save_dir_var.get():
            self._prompt_save_dir()
            if not self.save_dir_var.get():
                return
        self.run = Run(Path(self.save_dir_var.get()), datetime.datetime.now())
        self.t.delete("1.0", "end")

        for key, short, long in self.entry_guis:
            self.short_mapping[key.get()] = short.get()
            self.long_mapping[key.get()] = long.get()

        self.start_btn.grid_forget()
        self.save_btn.grid_forget()
        self.cancel_btn.grid(row=0, column=0, padx=5)
        self.time_info_var.set("0:00:00")
        self.path_info_var.set("")

        self.timer = RepeatTimer(1.0, lambda: update_time(self.time_info_var, self.run.start_time))
        self.timer.start()
        self.root.focus_set()

    def _is_recording(self):
        return self.timer and not self.timer.finished.is_set()

    def on_key_click(self, keysym):
        if keysym == "s":
            if self._is_recording():
                self.on_cancel()
            else:
                self.on_start()
        elif self._is_recording():
            self.record_event(keysym, self.short_mapping)

    def on_key_long_click(self, keysym):
        if self._is_recording():
            self.record_event(keysym, self.long_mapping)

    def on_cancel(self):
        try:
            path = self.run.save()
            self.path_info_var.set(f"Autosaved to: {str(path)}")
            self.save_btn.grid(row=0, column=2, padx=5)
        except FileNotFoundError:
            self.path_info_var.set("Failed to save file. Please check the save directory.")

        self.cancel_btn.grid_forget()
        self.start_btn.grid(row=0, column=0, padx=5)
        self.timer.cancel()

    def create_bottom(self):
        frame = ttk.Frame(self.root)

        self.start_btn = tk.Button(frame, text="Start", command=self.on_start,
                                   bg=COLORS["start"], activebackground=COLORS["start_active"],
                                   fg="white", activeforeground="white",
                                   font=(FONT, 11, "bold"), width=8, relief="flat", cursor="hand2")
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)

        self.cancel_btn = tk.Button(frame, text="Stop", command=self.on_cancel,
                                    bg=COLORS["stop"], activebackground=COLORS["stop_active"],
                                    fg="white", activeforeground="white",
                                    font=(FONT, 11, "bold"), width=8, relief="flat", cursor="hand2")

        time_label = ttk.Label(frame, textvariable=self.time_info_var, style="Timer.TLabel")
        self.time_info_var.set("0:00:00")
        time_label.grid(row=0, column=1, padx=15)

        self.save_btn = ttk.Button(frame, text="Save As", command=self.save_file)

        path_label = ttk.Label(frame, textvariable=self.path_info_var, style="Muted.TLabel")
        path_label.grid(row=1, column=0, columnspan=3, pady=(2, 0))

        frame.pack(padx=10, pady=(5, 10))
        return frame


def main():
    app = App()
    app.runloop()


if __name__ == "__main__":
    main()