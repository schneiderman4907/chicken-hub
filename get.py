import json
import time
import sys
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

OUT_FILE = "pinterest_data.json"


def is_relevant(text, keyword):
    if not text:
        return False
    return keyword.lower() in text.lower()


def scrape_pinterest(keyword: str):
    options = Options()

    # Linux Chrome profile
    options.add_argument(
        "--user-data-dir=/home/schneiderman/.config/google-chrome/pinterest_profile"
    )

    # Uncomment if you're using Chromium instead of Chrome
    # options.binary_location = "/usr/bin/chromium"

    driver = webdriver.Chrome(options=options)

    results = []
    seen = set()

    try:
        url = f"https://www.pinterest.com/search/pins/?q={quote_plus(keyword)}"
        driver.get(url)
        time.sleep(6)

        for _ in range(5):

            # PIN-LIKE CONTAINERS
            pins = driver.find_elements(By.CSS_SELECTOR, "a[href*='/pin/']")

            for pin in pins:
                try:
                    imgs = pin.find_elements(By.TAG_NAME, "img")
                    if not imgs:
                        continue

                    img = imgs[0]
                    src = img.get_attribute("src") or img.get_attribute("data-src")

                    if not src or "i.pinimg.com" not in src:
                        continue

                    alt = img.get_attribute("alt") or ""
                    aria = pin.get_attribute("aria-label") or ""

                    combined_text = f"{alt} {aria}"

                    if not is_relevant(combined_text, keyword):
                        continue

                    src = src.split("?")[0]

                    if src in seen:
                        continue

                    seen.add(src)

                    results.append({
                        "keyword": keyword,
                        "image": src,
                        "text": combined_text.strip()
                    })

                except Exception:
                    continue

            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(3)

        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

        print(f"Saved {len(results)} keyword-matched results for '{keyword}'")

    finally:
        driver.quit()


if __name__ == "__main__":
    query = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "chickens"
    )

    scrape_pinterest(query)
