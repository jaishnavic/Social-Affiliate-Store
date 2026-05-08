import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "products.json")


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