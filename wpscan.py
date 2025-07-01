import requests
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime
from urllib.parse import urljoin
import random
import re

# Konfigurasi
NUM_THREADS = 50
TIMEOUT = 10
OUTPUT_FILE = "wp.txt"

# Daftar User-Agent untuk acak
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
]

def get_random_headers():
    return {'User-Agent': random.choice(USER_AGENTS)}

def check_wordpress(site_url):
    if not site_url.startswith("http"):
        site_url = "http://" + site_url

    indicators = []

    try:
        # Halaman utama
        try:
            response = requests.get(site_url, headers=get_random_headers(), timeout=TIMEOUT)
            text = response.text.lower()
            if "wp-content" in text or "wp-includes" in text:
                indicators.append("wp-content/wp-includes")
            if re.search(r'<meta name=["\']generator["\'] content=["\']WordPress', text, re.IGNORECASE):
                indicators.append("meta generator")
        except:
            pass

        # wp-login.php
        try:
            resp = requests.get(urljoin(site_url, "/wp-login.php"), headers=get_random_headers(), timeout=TIMEOUT)
            if "user_login" in resp.text and resp.status_code == 200:
                indicators.append("wp-login.php")
        except:
            pass

        # wp-admin/
        try:
            resp = requests.get(urljoin(site_url, "/wp-admin/"), headers=get_random_headers(), timeout=TIMEOUT)
            if "dashboard" in resp.text or "wp-admin" in resp.text:
                indicators.append("wp-admin")
        except:
            pass

        # readme.html
        try:
            resp = requests.get(urljoin(site_url, "/readme.html"), headers=get_random_headers(), timeout=TIMEOUT)
            if "wordpress" in resp.text.lower():
                indicators.append("readme.html")
        except:
            pass

        # Output hasil
        if indicators:
            print(f"[✓] {site_url} -> WordPress")
            log_result(site_url)
        else:
            print(f"[x] {site_url} -> Bukan WordPress")

    except Exception as e:
        print(f"[!] {site_url} -> Error: {e}")

def log_result(url_only):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(url_only + "\n")

def load_urls_from_file(filename):
    try:
        with open(filename, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
            return urls
    except FileNotFoundError:
        print(f"[!] File '{filename}' tidak ditemukan.")
        return []

if __name__ == "__main__":
    urls = load_urls_from_file("meki.txt")

    if not urls:
        print("Tidak ada URL untuk diproses.")
    else:
        print("\n=== Scan dimulai:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "===\n")
        pool = ThreadPool(NUM_THREADS)
        pool.map(check_wordpress, urls)
        pool.close()
        pool.join()
        print("\n[✓] Selesai scanning. Hanya URL WordPress disimpan di 'wp.txt'.")
