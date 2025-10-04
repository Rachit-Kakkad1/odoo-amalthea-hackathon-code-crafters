from typing import Dict, Any
import logging
import asyncio
from datetime import datetime, timedelta
import httpx
from ..config import settings

logger = logging.getLogger(__name__)

REST_COUNTRIES_URL = settings.COUNTRIES_API_URL
EXCHANGE_RATE_URL_TEMPLATE = settings.EXCHANGE_API_URL

# Reusable async HTTP client
_http_client: httpx.AsyncClient | None = None

# Simple in-memory TTL caches
_countries_cache: dict[str, Any] = {"data": None, "expires_at": None}
_rates_cache: dict[str, dict[str, Any]] = {}

COUNTRIES_TTL = timedelta(hours=12)
RATES_TTL = timedelta(minutes=10)


async def _get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=10)
    return _http_client


async def init_http_clients() -> None:
    # Explicit initializer to be called on app startup
    await _get_client()


async def close_http_clients() -> None:
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


def _is_expired(expires_at: datetime | None) -> bool:
    if expires_at is None:
        return True
    return datetime.utcnow() >= expires_at


async def get_countries_and_currencies() -> Dict[str, Dict[str, str]]:
    if _countries_cache["data"] is not None and not _is_expired(_countries_cache["expires_at"]):
        return _countries_cache["data"]

    try:
        client = await _get_client()
        resp = await client.get(REST_COUNTRIES_URL)
        resp.raise_for_status()
        data = resp.json()

        result: Dict[str, Dict[str, str]] = {}
        for country in data:
            country_name = country["name"]["common"]
            currencies = country.get("currencies", {})
            if currencies:
                # Pick first currency entry deterministically
                code, details = next(iter(currencies.items()))
                result[country_name] = {
                    "code": code,
                    "name": details.get("name", code),
                }

        _countries_cache["data"] = result
        _countries_cache["expires_at"] = datetime.utcnow() + COUNTRIES_TTL
        logger.info("Fetched countries & currencies; cached %d entries", len(result))
        return result
    except Exception as exc:
        logger.error("Failed to fetch countries & currencies: %s", str(exc))
        raise RuntimeError(f"Failed to fetch countries & currencies: {str(exc)}")


async def get_currency_from_country(country_name: str) -> str:
    countries = await get_countries_and_currencies()
    entry = countries.get(country_name)
    if not entry:
        # Fallback to USD if not found
        return "USD"
    return entry["code"]


async def _get_rates(base_currency: str) -> Dict[str, float]:
    base = base_currency.upper()
    cached = _rates_cache.get(base)
    if cached and not _is_expired(cached.get("expires_at")):
        return cached["rates"]

    try:
        client = await _get_client()
        url = EXCHANGE_RATE_URL_TEMPLATE.format(base=base)
        headers = {"Authorization": f"Bearer {settings.EXCHANGE_API_KEY}"} if settings.EXCHANGE_API_KEY else {}
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        payload = resp.json()
        rates: Dict[str, float] = payload.get("rates", {})
        if not isinstance(rates, dict) or not rates:
            raise RuntimeError("Empty exchange rates payload")
        _rates_cache[base] = {"rates": rates, "expires_at": datetime.utcnow() + RATES_TTL}
        return rates
    except Exception as exc:
        logger.error("Failed to fetch exchange rates for %s: %s", base, str(exc))
        raise RuntimeError(f"Failed to fetch exchange rates for {base}: {str(exc)}")


async def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    if from_currency.upper() == to_currency.upper():
        return amount
    rates = await _get_rates(from_currency)
    target = to_currency.upper()
    if target not in rates:
        raise ValueError(f"Currency {to_currency} not found in exchange rates.")
    return amount * float(rates[target])


async def warm_caches() -> None:
    # Warm frequently used caches concurrently but non-fatal on error
    tasks = [
        get_countries_and_currencies(),
        _get_rates("USD"),
    ]
    try:
        await asyncio.gather(*tasks)
        logger.info("Currency service caches warmed")
    except Exception as exc:
        logger.warning("Cache warm-up encountered errors: %s", str(exc))