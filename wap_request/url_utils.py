from urllib.parse import urlparse

def ensure_http_scheme(url: str) -> str:
    url = url.strip()
    if not url:
        return url
    parsed = urlparse(url)
    if not parsed.scheme:
        return f"http://{url}"
    return url
