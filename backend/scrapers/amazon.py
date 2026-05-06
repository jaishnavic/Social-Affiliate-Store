import requests
from bs4 import BeautifulSoup

def scrape_amazon(url: str):
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    print(f"Amazon page content: {page.content}")

    try:
        name = soup.find("span", {"id": "productTitle"}).get_text().strip()
    except:
        name = "Unknown Product"

    try:
        price = soup.find("span", {"class": "a-price-whole"}).get_text().strip()
        price = float(price.replace(",", "").replace(".", ""))
    except:
        price = 0.0

    try:
        image = soup.find("img", {"id": "landingImage"})["src"]
    except:
        image = ""


    return {
        "name": name,
        "price": price,
        "image_url": image,
        "affiliate_url": url
    }