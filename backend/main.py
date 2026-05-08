from fastapi import FastAPI
from backend.scrapers.meesho import scrape_meesho
from backend.storage import add_product, load_products, save_products
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development (later restrict this)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API running"}

    
# 🔹 Preview product (NO SAVE)
@app.post("/preview-product")
def preview_product(data: dict):
    url = data.get("url")
    category = data.get("category", "general")

    scraped = scrape_meesho(url)
    scraped["category"] = category

    return scraped


# 🔹 Save product (after editing)
@app.post("/add-product")
def add_product_api(data: dict):
    product = add_product(data)
    return {"message": "Saved", "product": product}


# 🔹 Get all products
@app.get("/products")
def get_products():
    return load_products()


# 🔹 Update product
@app.put("/update-product/{product_id}")
def update_product(product_id: int, updated: dict):
    products = load_products()

    for p in products:
        if p["id"] == product_id:
            p.update(updated)

    save_products(products)
    return {"message": "Updated"}


# 🔹 Delete product
@app.delete("/delete-product/{product_id}")
def delete_product(product_id: int):
    products = load_products()
    products = [p for p in products if p["id"] != product_id]

    save_products(products)
    return {"message": "Deleted"}