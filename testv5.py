import os
import requests
import threading
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog

visited = set()
pause_flag = False
cancel_flag = False

def sanitize_filename(path):
    name = os.path.basename(path)
    if not name or '.' not in name:
        name = 'index.html' if path == '/' else path.strip('/').replace('/', '_') + '.html'
    return re.sub(r'[^\w\-_\.]', '_', name)

def get_asset_folder(asset_url):
    if asset_url.endswith('.css'):
        return 'assets/css'
    elif asset_url.endswith('.js'):
        return 'assets/js'
    elif asset_url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp')):
        return 'assets/images'
    else:
        return 'assets/other'

def download_asset(asset_url, base_folder):
    try:
        response = requests.get(asset_url, timeout=10)
        if response.status_code == 200:
            parsed_url = urlparse(asset_url)
            filename = os.path.basename(parsed_url.path)
            filename = re.sub(r'[^\w\-_\.]', '_', filename) or 'file'
            folder = get_asset_folder(asset_url)
            local_folder = os.path.join(base_folder, folder)
            os.makedirs(local_folder, exist_ok=True)
            local_path = os.path.join(local_folder, filename)
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return os.path.relpath(local_path, start=base_folder).replace('\\', '/')
    except:
        pass
    return None

def copy_page(url, base_folder, base_domain, update_progress):
    global visited, pause_flag, cancel_flag
    if url in visited or cancel_flag:
        return
    visited.add(url)

    while pause_flag:
        time.sleep(0.1)
        if cancel_flag:
            return

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        return

    for tag in soup.find_all(["img", "script", "link"]):
        attr = "src" if tag.name in ["img", "script"] else "href"
        if tag.has_attr(attr):
            asset_url = urljoin(url, tag[attr])
            local_asset_path = download_asset(asset_url, base_folder)
            if local_asset_path:
                tag[attr] = local_asset_path

    filename = sanitize_filename(urlparse(url).path)
    html_path = os.path.join(base_folder, filename)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    update_progress()

    for a_tag in soup.find_all("a", href=True):
        while pause_flag:
            time.sleep(0.1)
            if cancel_flag:
                return
        if cancel_flag:
            return
        link = urljoin(url, a_tag["href"])
        parsed_link = urlparse(link)
        if parsed_link.netloc == base_domain and parsed_link.scheme in ["http", "https"]:
            copy_page(link, base_folder, base_domain, update_progress)

def start_copy(website_url, target_folder, progress_callback, finish_callback):
    global visited, cancel_flag
    visited = set()
    cancel_flag = False
    os.makedirs(target_folder, exist_ok=True)
    domain = urlparse(website_url).netloc

    start_time = time.time()

    page_count = [0]

    def update_progress():
        page_count[0] += 1
        elapsed = time.time() - start_time
        estimated = (elapsed / page_count[0]) * (len(visited) + 1)
        remaining = max(0, estimated - elapsed)
        progress_callback(page_count[0], round(remaining))

    copy_page(website_url, target_folder, domain, update_progress)

    finish_callback()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Website Downloader")
        self.root.geometry("500x350")
        self.root.configure(bg="#1e1e1e")

        try:
            self.root.iconbitmap("logo.ico")
        except:
            pass

        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TButton", background="#2c2c2c", foreground="white")
        style.configure("TLabel", background="#1e1e1e", foreground="white")
        style.configure("TEntry", fieldbackground="#2c2c2c", foreground="white")
        style.configure("TProgressbar", background="#00ff00")

        ttk.Label(self.root, text="Website URL:").pack(pady=5)
        self.url_entry = ttk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)

        ttk.Label(self.root, text="Target Folder:").pack(pady=5)
        self.folder_entry = ttk.Entry(self.root, width=50)
        self.folder_entry.pack(pady=5)

        ttk.Button(self.root, text="Browse...", command=self.browse_folder).pack(pady=3)

        self.start_btn = ttk.Button(self.root, text="Start", command=self.start_download)
        self.start_btn.pack(pady=5)

        # self.pause_btn = ttk.Button(self.root, text="Pause", command=self.pause_download)
        # self.pause_btn.pack(pady=5)

        self.cancel_btn = ttk.Button(self.root, text="Cancel", command=self.cancel_download)
        self.cancel_btn.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, length=400, mode="indeterminate")
        self.progress.pack(pady=10)

        self.status_label = ttk.Label(self.root, text="")
        self.status_label.pack()

        ttk.Label(self.root, text="© Made by Md. Shahinur Islamm\nshahinalam6644@gmail.com", font=("Arial", 8),anchor="center",justify="center").pack(side="bottom", pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)

    def start_download(self):
        global pause_flag, cancel_flag
        pause_flag = False
        cancel_flag = False
        url = self.url_entry.get()
        folder = self.folder_entry.get()

        if not url or not folder:
            messagebox.showwarning("Warning", "Please enter both URL and folder name")
            return

        self.progress.start()
        self.status_label.config(text="Downloading...")

        def update_progress(pages, remaining):
            self.status_label.config(text=f"Downloaded {pages} page(s). Estimated time left: {remaining}s")

        def finish():
            self.progress.stop()
            self.status_label.config(text="✅ Download Complete")

        threading.Thread(target=start_copy, args=(url, folder, update_progress, finish), daemon=True).start()

    def pause_download(self):
        global pause_flag
        pause_flag = not pause_flag
        self.pause_btn.config(text="Resume" if pause_flag else "Pause")

    def cancel_download(self):
        global cancel_flag
        cancel_flag = True
        self.progress.stop()
        self.status_label.config(text="❌ Download Canceled")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
