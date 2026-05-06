from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_meesho(url: str):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)

            content = page.content()
            soup = BeautifulSoup(content, "html.parser")

            # Extract name
            try:
                name = soup.find("h1").get_text().strip()
            except:
                name = ""

            # Extract price
            try:
                price_tag = soup.find("h2")
                price = float(price_tag.get_text().replace("₹", "").replace(",", ""))
            except:
                price = 0.0

            # Extract image
            try:
                image = soup.find("img")["src"]
            except:
                image = ""

            browser.close()

            return {
                "name": name,
                "price": price,
                "image_url": image,
                "affiliate_url": url,
                "needs_manual": False if name else True
            }

    except:
        return {
            "name": "",
            "price": 0,
            "image_url": "",
            "affiliate_url": url,
            "needs_manual": True
        }