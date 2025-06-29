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

    # Process and download assets
    for tag in soup.find_all(["img", "script", "link"]):
        attr = "src" if tag.name in ["img", "script"] else "href"
        if tag.has_attr(attr):
            asset_url = urljoin(url, tag[attr])
            local_asset_path = download_asset(asset_url, base_folder)
            if local_asset_path:
                tag[attr] = local_asset_path

    # Save HTML file
    filename = sanitize_filename(urlparse(url).path)
    html_path = os.path.join(base_folder, filename)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"Saved {url} -> {html_path}")

    # Recursively follow internal links
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
start_copy("https://kfcbd.com", "kfc")
