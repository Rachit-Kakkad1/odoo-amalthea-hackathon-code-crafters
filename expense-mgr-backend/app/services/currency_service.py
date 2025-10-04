import requests
from typing import Dict
import logging
from ..config import settings

logger = logging.getLogger(__name__)

REST_COUNTRIES_URL = settings.COUNTRIES_API_URL
EXCHANGE_RATE_URL = settings.EXCHANGE_API_URL

def get_countries_and_currencies() -> Dict[str, Dict[str, str]]:
    try:
        resp = requests.get(REST_COUNTRIES_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        result = {}
        for country in data:
            country_name = country["name"]["common"]
            currencies = country.get("currencies", {})
            if currencies:
                for code, details in currencies.items():
                    result[country_name] = {
                        "code": code,
                        "name": details.get("name", code)
                    }
        logger.info(f"Successfully fetched {len(result)} countries and currencies")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch countries & currencies: {str(e)}")
        raise RuntimeError(f"Failed to fetch countries & currencies: {str(e)}")

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    try:
        url = EXCHANGE_RATE_URL.format(base=from_currency.upper())
        headers = {"Authorization": f"Bearer {settings.EXCHANGE_API_KEY}"} if settings.EXCHANGE_API_KEY else {}
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        rates = resp.json().get("rates", {})
        if to_currency.upper() not in rates:
            raise ValueError(f"Currency {to_currency} not found in exchange rates.")
        converted_amount = amount * rates[to_currency.upper()]
        logger.info(f"Converted {amount} {from_currency} to {converted_amount} {to_currency}")
        return converted_amount
    except Exception as e:
        logger.error(f"Currency conversion failed: {str(e)}")
        raise RuntimeError(f"Currency conversion failed: {str(e)}")