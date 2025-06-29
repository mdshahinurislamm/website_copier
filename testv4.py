import os
import threading
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

visited = set()
pause_flag = threading.Event()
cancel_flag = threading.Event()

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
    except Exception as e:
        print(f"Failed to download asset {asset_url}: {e}")
    return None

def copy_page(url, base_folder, base_domain, log_callback):
    if url in visited or cancel_flag.is_set():
        return
    visited.add(url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        log_callback(f"Failed to load {url}: {e}")
        return

    for tag in soup.find_all(["img", "script", "link"]):
        if cancel_flag.is_set():
            return
        while pause_flag.is_set():
            pause_flag.wait(1)

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
    log_callback(f"✅ Saved {url} -> {html_path}")

    for a_tag in soup.find_all("a", href=True):
        link = urljoin(url, a_tag["href"])
        parsed_link = urlparse(link)
        if parsed_link.netloc == base_domain and parsed_link.scheme in ["http", "https"]:
            copy_page(link, base_folder, base_domain, log_callback)

def start_copy(website_url, target_folder, log_callback):
    os.makedirs(target_folder, exist_ok=True)
    domain = urlparse(website_url).netloc
    visited.clear()
    copy_page(website_url, target_folder, domain, log_callback)
    log_callback("🎉 Copy complete!")

# GUI
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Website Copier")
        self.root.geometry("600x400")
        self.root.iconbitmap("logo.ico")

        self.root.configure(bg="#222")

        # URL
        tk.Label(root, text="Website URL:", fg="white", bg="#222").pack(pady=(10,0))
        self.url_entry = tk.Entry(root, width=60)
        self.url_entry.pack()

        # Folder
        tk.Label(root, text="Folder Name:", fg="white", bg="#222").pack(pady=(10,0))
        self.folder_entry = tk.Entry(root, width=60)
        self.folder_entry.pack()

        # Buttons
        frame = tk.Frame(root, bg="#222")
        frame.pack(pady=10)

        ttk.Style().theme_use('clam')
        self.start_btn = ttk.Button(frame, text="Start", command=self.run_copy)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = ttk.Button(frame, text="Pause", command=self.toggle_pause)
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.cancel_btn = ttk.Button(frame, text="Cancel", command=self.cancel_copy)
        self.cancel_btn.grid(row=0, column=2, padx=5)

        # Log box
        self.log_text = tk.Text(root, height=10, bg="#111", fg="lightgreen", wrap=tk.WORD)
        self.log_text.pack(padx=10, fill=tk.BOTH, expand=True)

        # Footer
        tk.Label(root, text="Made by Md. Shahinur Islam", bg="#222", fg="#aaa").pack(pady=5)

    def log(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

    def run_copy(self):
        cancel_flag.clear()
        pause_flag.clear()
        url = self.url_entry.get()
        folder = self.folder_entry.get()
        threading.Thread(target=start_copy, args=(url, folder, self.log), daemon=True).start()

    def toggle_pause(self):
        if pause_flag.is_set():
            pause_flag.clear()
            self.pause_btn.config(text="Pause")
        else:
            pause_flag.set()
            self.pause_btn.config(text="Resume")

    def cancel_copy(self):
        cancel_flag.set()
        self.log("⛔ Cancel requested.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
