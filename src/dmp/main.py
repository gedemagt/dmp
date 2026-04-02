import json
import os
import time
import tkinter as tk
import sys
from pathlib import Path

import datetime
from threading import Timer
from tkinter import filedialog

APP_NAME = "helenes_timer"

config = []


class Run:
    def __init__(self, start_time: datetime.datetime = None):
        self.events = []
        self.start_time = start_time

    def save_as(self, path: Path):
        old = self.save()
        os.rename(old, path)

    def save(self) -> Path:
        path = Path(self.start_time.strftime("%Y_%m_%d_%H_%M_%S.csv"))
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
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming" / APP_NAME
    elif sys.platform == "linux":
        return home / ".local/share" / APP_NAME
    elif sys.platform == "darwin":
        return home / "Library/Application Support" / APP_NAME
    else:
        raise Exception(f"Unsupported platform: {sys.platform}")


config_path = (get_datadir() / ".config").absolute()
if not os.path.exists(get_datadir().absolute()):
    os.mkdir(get_datadir().absolute())


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
    cfg = []
    for key, short, long in entry_guis:
        if key.get():
            cfg.append((key.get(), short.get(), long.get()))
    with open(config_path, "w+") as f:
        f.write(json.dumps(cfg))


def add_entry_row(frame, row, entry_guis: list, key_text="", short_text="", long_text=""):

    e1 = tk.Entry(frame, width=2)
    e1.insert(0, key_text)
    e1.grid(row=row, column=0)

    e2 = tk.Entry(frame)
    e2.grid(row=row, column=1)
    e2.insert(0, short_text)

    e3 = tk.Entry(frame)
    e3.grid(row=row, column=2)
    e3.insert(0, long_text)

    def remove():
        entry_guis.remove((e1, e2, e3))
        e1.grid_remove()
        e2.grid_remove()
        e3.grid_remove()
        add.grid_remove()
        frame.pack()
        save_config(entry_guis)

    add = tk.Button(frame, text="Delete", command=remove)
    add.grid(row=row, column=3)

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

        self.top_frame = self.create_top()
        self.mid_frame = self.create_middle()
        self.b1, self.b2, self.b3 = self.create_bottom()

        self.root.bind("<KeyRelease>", self.on_start_stop_key)

    def runloop(self):
        self.root.mainloop()

    def create_top(self):
        if not os.path.exists(config_path):
            data = [("", "", "")] * 3
        else:
            with open(config_path, "r") as f:
                data = json.loads(f.read())

        frame = tk.Frame(self.root)
        tk.Label(frame, text="Key").grid(row=0)
        tk.Label(frame, text="Short press").grid(row=0, column=1)
        tk.Label(frame, text="Long press").grid(row=0, column=2)
        self.entry_guis.clear()
        for idx, (key, short, long) in enumerate(data):
            add_entry_row(frame, idx + 1, self.entry_guis, key, short, long)

        add = tk.Button(frame, text="Add", command=lambda: add_entry_row(frame, len(self.entry_guis) + 1, self.entry_guis))
        add.grid(row=0, column=3)

        frame.pack()
        return frame

    def create_middle(self):
        frame = tk.Frame(self.root)
        self.t = tk.Text(frame, height=20)
        self.s = tk.Scrollbar(frame)
        self.s.pack(side=tk.RIGHT, fill=tk.Y)
        self.s.config(command=self.t.yview)
        self.t.pack(side=tk.LEFT, fill=tk.X)
        frame.pack()
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
        self.run = Run(datetime.datetime.now())
        self.t.delete("1.0", "end")

        for key, short, long in self.entry_guis:
            self.short_mapping[key.get()] = short.get()
            self.long_mapping[key.get()] = long.get()

        l = KeyBoardListener(self.top_frame)
        l.on_long_click(lambda x: self.record_event(x, self.long_mapping))
        l.on_click(lambda x: self.record_event(x, self.short_mapping))

        self.start_btn.grid_forget()
        self.save_btn.grid_forget()
        self.cancel_btn.grid(row=0, column=2)
        self.time_info_var.set("0:00:00")
        self.path_info_var.set("")

        self.timer = RepeatTimer(1.0, lambda: update_time(self.time_info_var, self.run.start_time))
        self.timer.start()
        self.top_frame.focus_set()

    def on_start_stop_key(self, e):
        if e.keysym == "s":
            if self.timer and not self.timer.finished.is_set():
                self.on_cancel()
            else:
                self.on_start()

    def on_cancel(self):
        path = self.run.save()
        self.path_info_var.set(f"Autosaved to: {str(path)}")
        self.cancel_btn.grid_forget()
        self.start_btn.grid(row=0, column=3)
        self.save_btn.grid(row=0, column=5)
        self.timer.cancel()

    def create_bottom(self):
        frame1 = tk.Frame(self.root)
        frame2 = tk.Frame(self.root)
        frame3 = tk.Frame(self.root)

        tt = tk.Label(frame2, textvariable=self.time_info_var)
        self.time_info_var.set("0:00:00")
        tt.grid(row=0, column=1)

        self.start_btn = tk.Button(frame1, text="Start", command=self.on_start)
        self.start_btn.grid(row=0, column=2)

        self.cancel_btn = tk.Button(frame1, text="Stop", command=self.on_cancel)

        self.save_btn = tk.Button(frame3, text="Save As", command=self.save_file)

        tt2 = tk.Label(frame3, textvariable=self.path_info_var)

        tt2.grid(row=0, column=4)

        frame1.pack()
        frame2.pack()
        frame3.pack()
        return frame1, frame2, frame3