import httpx

_HEADERS = {'Accept': 'text/vnd.wap.wml'}

_client: httpx.AsyncClient | None = None


def get_httpx_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=15.0)
    return _client


async def close_httpx_client():
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()
        _client = None


async def request_wap(client: httpx.AsyncClient, url: str) -> tuple[int, str]:
    resp = await client.get(url, headers=_HEADERS)
    return resp.status_code, resp.text