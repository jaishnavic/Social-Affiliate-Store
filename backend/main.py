from fastapi import FastAPI
from scrapers.meesho import scrape_meesho
from scrapers.instagram import fetch_instagram_thumbnail, debug_fetch
from storage import (
    add_product, load_products, save_products, get_product_by_id,
    add_reel, load_reels, save_reels, attach_products_to_reel
)
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


# ================= PRODUCTS =================

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


# 🔹 Get single product (used by reel viewer / product detail links)
@app.get("/product/{product_id}")
def get_product(product_id: int):
    product = get_product_by_id(product_id)
    if not product:
        return {"error": "Not found"}
    return product


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


# ================= REELS =================

# 🔹 Save a reel (video + tagged products)
@app.post("/add-reel")
def add_reel_api(data: dict):
    video_url = data.get("video_url", "") or ""

    if not data.get("thumbnail_url") and "instagram.com" in video_url:
        thumbnail = fetch_instagram_thumbnail(video_url)
        if thumbnail:
            data["thumbnail_url"] = thumbnail

    reel = add_reel(data)
    return {"message": "Saved", "reel": reel}


# 🔹 One-time helper: backfill thumbnails for existing Instagram reels
# that were saved before this feature existed / where the fetch failed
@app.post("/backfill-thumbnails")
def backfill_thumbnails():
    reels = load_reels()
    updated = 0

    for r in reels:
        video_url = r.get("video_url", "") or ""
        if not r.get("thumbnail_url") and "instagram.com" in video_url:
            thumbnail = fetch_instagram_thumbnail(video_url)
            if thumbnail:
                r["thumbnail_url"] = thumbnail
                updated += 1

    save_reels(reels)
    return {"message": "Backfill complete", "updated": updated, "total": len(reels)}


# 🔹 Diagnostic: see exactly what Instagram sent back for a given URL
@app.get("/debug-instagram-thumbnail")
def debug_instagram_thumbnail(url: str):
    return debug_fetch(url)


# 🔹 Get all reels, each with its tagged products joined in
@app.get("/reels")
def get_reels():
    reels = load_reels()
    return [attach_products_to_reel(r) for r in reels]


# 🔹 Get a single reel with tagged products joined in
@app.get("/reel/{reel_id}")
def get_reel(reel_id: int):
    reels = load_reels()
    for r in reels:
        if r["id"] == reel_id:
            return attach_products_to_reel(r)
    return {"error": "Not found"}


# 🔹 Update reel (edit caption, category, swap tagged products, etc.)
@app.put("/update-reel/{reel_id}")
def update_reel(reel_id: int, updated: dict):
    reels = load_reels()

    for r in reels:
        if r["id"] == reel_id:
            r.update(updated)

    save_reels(reels)
    return {"message": "Updated"}


# 🔹 Delete reel
@app.delete("/delete-reel/{reel_id}")
def delete_reel(reel_id: int):
    reels = load_reels()
    reels = [r for r in reels if r["id"] != reel_id]

    save_reels(reels)
    return {"message": "Deleted"}