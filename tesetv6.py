import os
import asyncio
from urllib.parse import urlparse, urljoin
from playwright.async_api import async_playwright

URL = "https://themegavias.com/wp/kipso/home-2"  # Your target URL
OUTPUT_DIR = "downloaded_site"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create subfolders for assets
ASSET_FOLDERS = {
    "text/css": "css",
    "application/javascript": "js",
    "text/javascript": "js",
    "image/": "img",
    "font/": "fonts",
    "application/font-woff": "fonts",
}

for folder in set(ASSET_FOLDERS.values()):
    os.makedirs(os.path.join(OUTPUT_DIR, folder), exist_ok=True)

# Map original URL to local relative path (with folders)
downloaded_files = {}

def sanitize_filename(url):
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    if not name or '.' not in name:
        name = "index.html"
    if "?" in name:
        name = name.split("?")[0]
    return name

def get_asset_folder(content_type):
    for key in ASSET_FOLDERS:
        if content_type.startswith(key):
            return ASSET_FOLDERS[key]
    return ""

async def save_response_content(response, filename, folder=""):
    path = os.path.join(OUTPUT_DIR, folder, filename) if folder else os.path.join(OUTPUT_DIR, filename)
    try:
        content = await response.body()
        with open(path, "wb") as f:
            f.write(content)
        # Return path relative to OUTPUT_DIR for HTML rewriting
        return os.path.join(folder, filename).replace("\\", "/") if folder else filename
    except Exception as e:
        print(f"Failed to save {filename}: {e}")
        return None

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

        page = await context.new_page()

        async def handle_response(response):
            url = response.url
            if url.startswith("data:"):
                return
            content_type = response.headers.get("content-type", "")
            if any(x in content_type for x in ["text/css", "application/javascript", "text/javascript",
                                               "image/", "font/", "application/font-woff", "text/html"]):
                filename = sanitize_filename(url)
                folder = get_asset_folder(content_type)
                if url not in downloaded_files:
                    saved_path = await save_response_content(response, filename, folder)
                    if saved_path:
                        downloaded_files[url] = saved_path

        page.on("response", handle_response)

        print(f"Loading page: {URL}")
        await page.goto(URL, wait_until="networkidle")

        html = await page.content()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Fix src attributes
        for tag in soup.find_all(src=True):
            src_url = urljoin(URL, tag['src'])
            if src_url in downloaded_files:
                tag['src'] = downloaded_files[src_url]

        # Fix href attributes
        for tag in soup.find_all(href=True):
            href_url = urljoin(URL, tag['href'])
            if href_url in downloaded_files:
                tag['href'] = downloaded_files[href_url]

        # Save fixed HTML
        with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(str(soup))

        print("✅ Download complete!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
