import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from decouple import config

FMP_BASE = "https://financialmodelingprep.com/stable"
_API_KEY = None


def _key():
    global _API_KEY
    if _API_KEY is None:
        _API_KEY = config("FMP_API_KEY", default="")
    return _API_KEY


def fmp_get(endpoint, params=None):
    url = f"{FMP_BASE}{endpoint}"
    p = {"apikey": _key()}
    if params:
        p.update(params)
    resp = requests.get(url, params=p, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _fetch_one_quote(symbol):
    """Fetch a single symbol quote. Returns the first item or None."""
    try:
        data = fmp_get("/quote", {"symbol": symbol})
        if isinstance(data, list) and data:
            return data[0]
    except Exception:
        pass
    return None


def get_quotes(symbols):
    """
    Fetch quotes for a list of symbols in parallel.
    Starter plan does not support batch-quote, so we fetch individually.
    Returns list of quote dicts (same shape as old v3 batch response).
    """
    if not symbols:
        return []
    results = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(_fetch_one_quote, sym): sym for sym in symbols}
        for future in as_completed(futures):
            quote = future.result()
            if quote:
                results.append(quote)
    return results


def search_symbols(query, limit=15):
    """Search FMP for symbols by ticker or company name. Returns [{symbol, name}]."""
    try:
        results = fmp_get("/search-symbol", {"query": query, "limit": limit})
        if isinstance(results, list):
            return [
                {"symbol": r.get("symbol", ""), "name": r.get("name", "")}
                for r in results if r.get("symbol")
            ]
    except Exception:
        pass
    return []


def get_news(feed_type="stock", limit=50):
    """
    Fetch latest news from FMP stable API.
    feed_type: 'stock' | 'forex' | 'crypto'
    Note: 'general' is not available on the Starter plan.
    """
    endpoints = {
        "stock":  "/news/stock-latest",
        "forex":  "/news/forex-latest",
        "crypto": "/news/crypto-latest",
    }
    endpoint = endpoints.get(feed_type, "/news/stock-latest")
    return fmp_get(endpoint, {"limit": limit})
