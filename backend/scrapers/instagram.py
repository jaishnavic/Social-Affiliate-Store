import json
import re
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def _extract_thumbnail_from_html(html: str):
    # property="og:image" content="..."  (old-style server-rendered pages)
    match = re.search(r'property="og:image"\s+content="([^"]+)"', html)
    if not match:
        match = re.search(r'content="([^"]+)"\s+property="og:image"', html)
    if match:
        return match.group(1).replace("&amp;", "&")

    # Twitter card image, sometimes present even when og:image isn't
    match = re.search(r'name="twitter:image"\s+content="([^"]+)"', html)
    if match:
        return match.group(1).replace("&amp;", "&")

    # Modern Instagram embeds the photo/video thumbnail as escaped JSON
    # inside the page's data payload, e.g. "display_url":"https:\/\/..."
    match = re.search(r'"display_url"\s*:\s*"([^"]+)"', html)
    if match:
        return match.group(1).replace("\\/", "/").replace("&amp;", "&")

    # Structured data block Instagram includes for search engines
    ld_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    if ld_match:
        try:
            data = json.loads(ld_match.group(1))
            image = data.get("image")
            if isinstance(image, list) and image:
                return image[0]
            if isinstance(image, str):
                return image
        except (json.JSONDecodeError, AttributeError):
            pass

    return None


def fetch_instagram_thumbnail(url: str):
    """
    Scrapes a thumbnail image for a public Instagram reel/post page.
    Tries og:image, twitter:image, the embedded display_url JSON field,
    and the ld+json structured data block, in that order.
    Returns the thumbnail URL, or None if none of them were found
    (private post, login-wall response, Instagram rate-limiting, etc).
    """
    try:
        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code != 200:
            return None

        return _extract_thumbnail_from_html(res.text)

    except requests.RequestException:
        return None


def debug_fetch(url: str):
    """
    Diagnostic helper: returns raw info about what Instagram sent back,
    so we can tell whether it's a login-wall, a block, or a markup change.
    """
    try:
        res = requests.get(url, headers=HEADERS, timeout=8)
        html = res.text
        has_login_wall = "loginForm" in html or "Log in to Instagram" in html or "/accounts/login" in html

        return {
            "status_code": res.status_code,
            "html_length": len(html),
            "looks_like_login_wall": has_login_wall,
            "contains_og_image_tag": "og:image" in html,
            "contains_twitter_image_tag": "twitter:image" in html,
            "contains_display_url_field": '"display_url"' in html,
            "contains_ld_json_block": 'application/ld+json' in html,
            "resolved_thumbnail": _extract_thumbnail_from_html(html),
        }
    except requests.RequestException as e:
        return {"error": str(e)}