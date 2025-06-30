import requests
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime

# Jumlah thread paralel yang akan digunakan
NUM_THREADS = 10
TIMEOUT = 20
OUTPUT_FILE = "wp.txt"

def check_wordpress(site_url):
    if not site_url.startswith("http"):
        site_url = "http://" + site_url

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(site_url, headers=headers, timeout=TIMEOUT)

        if "wp-content" in response.text or "wp-includes" in response.text:
            result = f"[✓] {site_url} menggunakan WordPress."
        else:
            result = f"[x] {site_url} kemungkinan TIDAK menggunakan WordPress."
    except Exception as e:
        result = f"[!] Gagal mengakses {site_url}: {e}"

    print(result)
    log_result(result)
    return result

def log_result(text):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(text + "\n")

def load_urls_from_file(filename):
    try:
        with open(filename, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
            return urls
    except FileNotFoundError:
        print(f"[!] File '{filename}' tidak ditemukan.")
        return []

if __name__ == "__main__":
    urls = load_urls_from_file("url.txt")

    if not urls:
        print("Tidak ada URL untuk diproses.")
    else:
        header = "\n=== Scan dimulai: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " ==="
        log_result(header)
        print(header)

        # Jalankan scanner dengan thread pool
        pool = ThreadPool(NUM_THREADS)
        pool.map(check_wordpress, urls)
        pool.close()
        pool.join()

        print("\nSelesai scanning semua URL.")
