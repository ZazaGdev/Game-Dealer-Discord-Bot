# api/itad_client.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
from .http import HttpClient
from models import Deal

class ITADClient:
    BASE = "https://api.isthereanydeal.com"  # adjust to real base

    def __init__(self, api_key: Optional[str] = None, http: Optional[HttpClient] = None):
        headers = {}
        self.http = http or HttpClient(headers=headers)
        self.api_key = api_key

    async def close(self) -> None:
        await self.http.close()

    async def fetch_deals(self, *, min_discount: int = 60, limit: int = 10) -> List[Deal]:
        """
        Example method: fetch recent deals, normalize to our Deal model.
        """
        # Example params — change to match real ITAD endpoints
        params: Dict[str, Any] = {
            "key": self.api_key,
            "minDiscount": min_discount,
            "limit": limit,
        }
        data = await self.http.get_json(f"{self.BASE}/v01/deals/list/", params=params)

        # --- transform into our internal Deal model ---
        deals: List[Deal] = []
        items = data.get("data", []) if isinstance(data, dict) else []
        for item in items:
            title = item.get("title") or "Game Deal"
            store = item.get("shop", {}).get("name", "Unknown Store")
            url = item.get("urls", {}).get("buy", "")
            current = item.get("price_new")
            old = item.get("price_old")
            discount_pct = item.get("price_cut")
            deal: Deal = {
                "title": title,
                "price": f"${current:.2f}" if isinstance(current, (int, float)) else str(current or "Unknown"),
                "store": store,
                "url": url or "",
                "discount": f"{discount_pct}%" if discount_pct is not None else None,
                "original_price": f"${old:.2f}" if isinstance(old, (int, float)) else (str(old) if old else None),
            }
            deals.append(deal)
        return deals
