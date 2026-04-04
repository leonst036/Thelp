import os
import requests
import tkinter as tk
from tkinter import messagebox
import webbrowser

# Current version of Thelp
VERSION = "v1.0.0"

def check_for_updates():
    if os.getenv("CHECK_UPDATES", "true").lower() == "false":
        return
    try:
        response = requests.get("https://api.github.com/repos/leonst036/Thelp/releases/latest", timeout=3)
        if response.status_code == 200:
            latest_version = response.json().get("tag_name")
            if latest_version and latest_version != VERSION:
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                if messagebox.askyesno("Update Available", f"A new version of Thelp ({latest_version}) is available!\nYour version: {VERSION}\n\nDo you want to download the update?", parent=root):
                    webbrowser.open("https://github.com/leonst036/Thelp/releases/latest")
                root.destroy()
    except Exception:
        pass

