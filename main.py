import os
import requests
from bs4 import BeautifulSoup

URL = os.getenv("SCRAPE_URL", "https://example.com")

def main():
    r = requests.get(URL, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")
    title = soup.title.string if soup.title else "Sin título"
    print(title)

if __name__ == "__main__":
    main()
