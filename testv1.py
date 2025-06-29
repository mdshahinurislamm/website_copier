import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

visited = set()

def sanitize_filename(path):
    name = os.path.basename(path)
    if not name or '.' not in name:
        name = 'index.html' if path == '/' else path.strip('/').replace('/', '_') + '.html'
    return re.sub(r'[^\w\-_\.]', '_', name)

def get_asset_folder(asset_url):
    if asset_url.endswith(('.css')):
        return 'assets/css'
    elif asset_url.endswith(('.js')):
        return 'assets/js'
    elif asset_url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp')):
        return 'assets/images'
    else:
        return 'assets/other'

def download_asset(asset_url, folder):
    try:
        response = requests.get(asset_url, timeout=10)
        if response.status_code == 200:
            os.makedirs(folder, exist_ok=True)
            parsed_url = urlparse(asset_url)
            filename = os.path.basename(parsed_url.path)
            filename = re.sub(r'[^\w\-_\.]', '_', filename) or "file"
            local_path = os.path.join(folder, filename)
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return os.path.relpath(local_path, start=".")
    except:
        pass
    return None

def copy_page(url, base_folder, base_domain):
    if url in visited:
        return
    visited.add(url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Failed to load {url}: {e}")
        return

    # Download assets and rewrite links
    for tag in soup.find_all(["img", "script", "link"]):
        attr = "src" if tag.name != "link" else "href"
        if tag.has_attr(attr):
            asset_url = urljoin(url, tag[attr])
            folder = get_asset_folder(asset_url)
            local_asset_path = download_asset(asset_url, os.path.join(base_folder, folder))
            if local_asset_path:
                tag[attr] = local_asset_path.replace("\\", "/")

    # Save the HTML file to the root of base_folder
    filename = sanitize_filename(urlparse(url).path)
    html_path = os.path.join(base_folder, filename)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print(f"Saved {url} -> {filename}")


    # Recursively copy internal links
    for a_tag in soup.find_all("a", href=True):
        link = urljoin(url, a_tag["href"])
        parsed_link = urlparse(link)
        if parsed_link.netloc == base_domain and parsed_link.scheme in ["http", "https"]:
            copy_page(link, base_folder, base_domain)

def start_copy(website_url, target_folder):
    os.makedirs(target_folder, exist_ok=True)
    domain = urlparse(website_url).netloc
    copy_page(website_url, target_folder, domain)
    print(f"🎉 Copy complete! Check the '{target_folder}' folder.")

# ==== USAGE ====
start_copy("https://marketifythemes.net/tailwind/orido/index.html", "it")
