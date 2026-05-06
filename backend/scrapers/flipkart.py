import json
from playwright.sync_api import sync_playwright

def scrape_flipkart(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        # Extract JSON-LD structured data
        product_data = {}
        try:
            json_ld = page.locator("script[type='application/ld+json']").nth(0).inner_text()
            data = json.loads(json_ld)
            if isinstance(data, list):
                data = data[0]  # Flipkart often wraps in a list

            product_data["name"] = data.get("name", "Unknown Product")
            product_data["price"] = data.get("offers", {}).get("price", 0.0)
            product_data["image_url"] = data.get("image", [""])[0]
        except Exception as e:
            product_data["name"] = "Unknown Product"
            product_data["price"] = 0.0
            product_data["image_url"] = ""

        browser.close()

        return {
            "name": product_data["name"],
            "price": float(product_data["price"]),
            "image_url": product_data["image_url"],
            "affiliate_url": url
        }