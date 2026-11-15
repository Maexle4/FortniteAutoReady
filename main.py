import os
import sys
import threading
import time
import tkinter as tk
from tkinter import colorchooser, messagebox

import pyautogui
import keyboard
from PIL import Image, ImageDraw
import pystray

pyautogui.FAILSAFE = True

class AutoPlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fortnite Auto Ready")
        self.root.geometry("420x470")
        self.root.resizable(False, False)

        self.running = False
        self.hotkey = "f8"
        self.registered_hotkey = None
        self.tray_icon = None

        # Standard-Startkoordinaten
        self.lobby_x = 240
        self.lobby_y = 872
        self.postgame_x = 1575
        self.postgame_y = 550

        self.target_rgb = (222, 228, 17)

        self._build_ui()
        self._setup_hotkey()

        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def _build_ui(self):
        # --- FARB-PICKER SEKTION ---
        tk.Label(self.root, text="Zielfarbe (Button-Farbe):", font=("Arial", 10, "bold")).pack(pady=(10, 2))
        frame_color = tk.Frame(self.root)
        frame_color.pack(pady=2)

        self.color_box = tk.Label(frame_color, text="    ", bg=self._rgb_to_hex(self.target_rgb), width=8, relief="sunken")
        self.color_box.pack(side="left", padx=5)

        btn_pick_color = tk.Button(frame_color, text="Farbe wählen", command=self.pick_color)
        btn_pick_color.pack(side="left", padx=5)

        # --- LOBBY SEKTION ---
        tk.Label(self.root, text="Lobby-Button (X, Y):", font=("Arial", 10, "bold")).pack(pady=(10, 2))
        frame_lobby = tk.Frame(self.root)
        frame_lobby.pack(pady=2)

        tk.Label(frame_lobby, text="X:").pack(side="left", padx=2)
        self.entry_lobby_x = tk.Entry(frame_lobby, justify="center", width=6)
        self.entry_lobby_x.insert(0, str(self.lobby_x))
        self.entry_lobby_x.pack(side="left", padx=3)

        tk.Label(frame_lobby, text="Y:").pack(side="left", padx=2)
        self.entry_lobby_y = tk.Entry(frame_lobby, justify="center", width=6)
        self.entry_lobby_y.insert(0, str(self.lobby_y))
        self.entry_lobby_y.pack(side="left", padx=3)

        btn_pick_lobby = tk.Button(frame_lobby, text="Maus-Pos erfassen", command=lambda: self.pick_position("lobby"))
        btn_pick_lobby.pack(side="left", padx=5)

        # --- POSTGAME SEKTION ---
        tk.Label(self.root, text="Postgame-Button (X, Y):", font=("Arial", 10, "bold")).pack(pady=(10, 2))
        frame_postgame = tk.Frame(self.root)
        frame_postgame.pack(pady=2)

        tk.Label(frame_postgame, text="X:").pack(side="left", padx=2)
        self.entry_postgame_x = tk.Entry(frame_postgame, justify="center", width=6)
        self.entry_postgame_x.insert(0, str(self.postgame_x))
        self.entry_postgame_x.pack(side="left", padx=3)

        tk.Label(frame_postgame, text="Y:").pack(side="left", padx=2)
        self.entry_postgame_y = tk.Entry(frame_postgame, justify="center", width=6)
        self.entry_postgame_y.insert(0, str(self.postgame_y))
        self.entry_postgame_y.pack(side="left", padx=3)

        btn_pick_postgame = tk.Button(frame_postgame, text="Maus-Pos erfassen", command=lambda: self.pick_position("postgame"))
        btn_pick_postgame.pack(side="left", padx=5)

        btn_save_pos = tk.Button(self.root, text="Koordinaten übernehmen", command=self.save_positions)
        btn_save_pos.pack(pady=8)

        # --- HOTKEY SEKTION ---
        tk.Label(self.root, text="Hotkey (Ein/Aus):", font=("Arial", 10, "bold")).pack(pady=(5, 2))
        frame_hotkey = tk.Frame(self.root)
        frame_hotkey.pack(pady=2)

        self.entry_hotkey = tk.Entry(frame_hotkey, justify="center", width=10)
        self.entry_hotkey.insert(0, self.hotkey)
        self.entry_hotkey.pack(side="left", padx=5)

        btn_set_key = tk.Button(frame_hotkey, text="Speichern", command=self._setup_hotkey)
        btn_set_key.pack(side="left")

        # --- STATUS ---
        self.lbl_status = tk.Label(self.root, text="Status: INAKTIV", fg="red", font=("Arial", 11, "bold"))
        self.lbl_status.pack(pady=(15, 5))

    def _rgb_to_hex(self, rgb):
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def pick_color(self):
        color = colorchooser.askcolor(title="Wähle die Button-Farbe", initialcolor=self._rgb_to_hex(self.target_rgb))
        if color[0]:
            self.target_rgb = tuple(int(c) for c in color[0])
            self.color_box.config(bg=self._rgb_to_hex(self.target_rgb))

    def pick_position(self, pos_type):
        self.lbl_status.config(text=f"Status: Bewege Maus auf {pos_type.capitalize()} (3 Sek)...", fg="orange")
        self.root.update()

        def do_pick():
            time.sleep(3)
            x, y = pyautogui.position()
            self.root.after(0, lambda: self._update_entry_fields(pos_type, x, y))

        threading.Thread(target=do_pick, daemon=True).start()

    def _update_entry_fields(self, pos_type, x, y):
        if pos_type == "lobby":
            self.entry_lobby_x.delete(0, tk.END)
            self.entry_lobby_x.insert(0, str(x))
            self.entry_lobby_y.delete(0, tk.END)
            self.entry_lobby_y.insert(0, str(y))
            self.lobby_x = x
            self.lobby_y = y
        elif pos_type == "postgame":
            self.entry_postgame_x.delete(0, tk.END)
            self.entry_postgame_x.insert(0, str(x))
            self.entry_postgame_y.delete(0, tk.END)
            self.entry_postgame_y.insert(0, str(y))
            self.postgame_x = x
            self.postgame_y = y

        self.lbl_status.config(text="Status: INAKTIV", fg="red")
        messagebox.showinfo("Erfolg", f"Position für {pos_type.capitalize()} gespeichert!\nX: {x}, Y: {y}")

    def save_positions(self):
        try:
            self.lobby_x = int(self.entry_lobby_x.get())
            self.lobby_y = int(self.entry_lobby_y.get())
            self.postgame_x = int(self.entry_postgame_x.get())
            self.postgame_y = int(self.entry_postgame_y.get())
            messagebox.showinfo("Erfolg", "Koordinaten erfolgreich aktualisiert!")
        except ValueError:
            messagebox.showerror("Fehler", "Bitte nur Ganzzahlen für X und Y eingeben!")

    def toggle(self):
        self.running = not self.running
        if self.running:
            self.lbl_status.config(text="Status: AKTIV", fg="green")
            threading.Thread(target=self.scan_and_click, daemon=True).start()
        else:
            self.lbl_status.config(text="Status: INAKTIV", fg="red")

    def _setup_hotkey(self):
        new_key = self.entry_hotkey.get().strip().lower()
        if not new_key:
            return

        try:
            if self.registered_hotkey:
                keyboard.remove_hotkey(self.registered_hotkey)
            self.registered_hotkey = keyboard.add_hotkey(new_key, self.toggle)
            self.hotkey = new_key
        except Exception as e:
            messagebox.showerror("Fehler", f"Ungültiger Hotkey: {e}")

    def scan_and_click(self):
        while self.running:
            try:
                # 1. Prüfe Lobby-Position auf die Zielfarbe (mit Toleranz von 15)
                pixel_lobby = pyautogui.pixel(self.lobby_x, self.lobby_y)
                if all(abs(pixel_lobby[i] - self.target_rgb[i]) < 15 for i in range(3)):
                    pyautogui.click(self.lobby_x, self.lobby_y)
                    time.sleep(1.0)
                    continue

                # 2. Prüfe Postgame-Position auf die Zielfarbe
                pixel_postgame = pyautogui.pixel(self.postgame_x, self.postgame_y)
                if all(abs(pixel_postgame[i] - self.target_rgb[i]) < 15 for i in range(3)):
                    pyautogui.click(self.postgame_x, self.postgame_y)
                    time.sleep(1.0)
                    continue

            except Exception:
                pass

            time.sleep(0.4)

    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color=(30, 30, 30))
        draw = ImageDraw.Draw(image)
        draw.ellipse((12, 12, 52, 52), fill=(235, 238, 52))
        return image

    def hide_to_tray(self):
        self.root.withdraw()

        menu = pystray.Menu(
            pystray.MenuItem("Öffnen", self.show_from_tray, default=True),
            pystray.MenuItem("Ein / Aus", self.toggle),
            pystray.MenuItem("Beenden", self.quit_app)
        )

        self.tray_icon = pystray.Icon("FortniteAutoReady", self.create_tray_icon(), "Fortnite Auto Ready", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.deiconify)

    def quit_app(self, icon=None, item=None):
        self.running = False
        if self.registered_hotkey:
            keyboard.remove_hotkey(self.registered_hotkey)
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoPlayApp(root)
    root.mainloop()