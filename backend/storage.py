import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "products.json")
REELS_FILE_PATH = os.path.join(BASE_DIR, "reels.json")


# ================= PRODUCTS =================

def load_products():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r") as f:
        return json.load(f)


def save_products(products):
    with open(FILE_PATH, "w") as f:
        json.dump(products, f, indent=2)


def add_product(product):
    products = load_products()

    product["id"] = len(products) + 1
    product["created_at"] = datetime.now().isoformat()

    products.append(product)
    save_products(products)

    return product


def get_product_by_id(product_id):
    products = load_products()
    for p in products:
        if p["id"] == product_id:
            return p
    return None


# ================= REELS =================

def load_reels():
    if not os.path.exists(REELS_FILE_PATH):
        return []
    with open(REELS_FILE_PATH, "r") as f:
        return json.load(f)


def save_reels(reels):
    with open(REELS_FILE_PATH, "w") as f:
        json.dump(reels, f, indent=2)


def add_reel(reel):
    reels = load_reels()

    reel["id"] = len(reels) + 1
    reel["created_at"] = datetime.now().isoformat()
    reel.setdefault("product_ids", [])

    reels.append(reel)
    save_reels(reels)

    return reel


def attach_products_to_reel(reel):
    """Joins full product objects onto a reel based on its product_ids."""
    products = load_products()
    product_ids = set(reel.get("product_ids", []))

    reel_with_products = dict(reel)
    reel_with_products["products"] = [p for p in products if p["id"] in product_ids]

    return reel_with_products
