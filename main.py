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
        self.root.geometry("380x300")
        self.root.resizable(False, False)

        self.running = False
        self.target_rgb = (222, 228, 17)
        self.hotkey = "f8"
        self.registered_hotkey = None
        self.tray_icon = None

        self._build_ui()
        self._setup_hotkey()

        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def _build_ui(self):
        tk.Label(self.root, text="Zielfarbe für 'Spielen'-Button:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        self.color_box = tk.Label(self.root, text="  ", bg=self._rgb_to_hex(self.target_rgb), width=14, relief="sunken")
        self.color_box.pack(pady=5)

        btn_pick = tk.Button(self.root, text="Farbe wählen", command=self.pick_color)
        btn_pick.pack(pady=5)

        tk.Label(self.root, text="Hotkey (Ein/Aus):", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        frame_hotkey = tk.Frame(self.root)
        frame_hotkey.pack(pady=5)

        self.entry_hotkey = tk.Entry(frame_hotkey, justify="center", width=10)
        self.entry_hotkey.insert(0, self.hotkey)
        self.entry_hotkey.pack(side="left", padx=5)

        btn_set_key = tk.Button(frame_hotkey, text="Speichern", command=self._setup_hotkey)
        btn_set_key.pack(side="left")

        self.lbl_status = tk.Label(self.root, text="Status: INAKTIV", fg="red", font=("Arial", 11, "bold"))
        self.lbl_status.pack(pady=(15, 5))

    def _rgb_to_hex(self, rgb):
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def pick_color(self):
        color = colorchooser.askcolor(title="Wähle die Button-Farbe")
        if color[0]:
            self.target_rgb = tuple(int(c) for c in color[0])
            self.color_box.config(bg=self._rgb_to_hex(self.target_rgb))

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
            #messagebox.showinfo("Hotkey", f"Hotkey auf '{self.hotkey.upper()}' gesetzt.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Ungültiger Hotkey: {e}")

    def scan_and_click(self):
        screen_width, screen_height = pyautogui.size()

        # Suchbereich unten links
        search_region = (0, int(screen_height * 0.6), int(screen_width * 0.3), int(screen_height * 0.4))

        while self.running:
            try:
                screenshot = pyautogui.screenshot(region=search_region)
                found = False

                for x in range(0, screenshot.width, 6):
                    for y in range(0, screenshot.height, 6):
                        pixel_color = screenshot.getpixel((x, y))[:3]

                        if all(abs(pixel_color[i] - self.target_rgb[i]) < 15 for i in range(3)):
                            click_x = search_region[0] + x
                            click_y = search_region[1] + y

                            pyautogui.moveTo(click_x, click_y, duration=0.15, tween=pyautogui.easeOutQuad)
                            time.sleep(0.05)
                            pyautogui.click()

                            found = True
                            time.sleep(0.5)
                            break
                    if found:
                        break
            except Exception:
                pass

            time.sleep(0.5)

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