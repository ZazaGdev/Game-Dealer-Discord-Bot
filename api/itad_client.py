# api/itad_client.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
from .http import HttpClient
from models import Deal

class ITADClient:
    BASE = "https://api.isthereanydeal.com"

    def __init__(self, api_key: Optional[str] = None, http: Optional[HttpClient] = None):
        headers = {}
        self.http = http or HttpClient(headers=headers)
        self.api_key = api_key

    async def close(self) -> None:
        await self.http.close()

    async def fetch_deals(self, *, min_discount: int = 60, limit: int = 10) -> List[Deal]:
        """
        Fetch deals using the correct ITAD API endpoints
        """
        if not self.api_key:
            raise ValueError("ITAD API key is required")

        # Use the correct ITAD API endpoint - deals/v2
        params: Dict[str, Any] = {
            "key": self.api_key,
            "offset": 0,
            "limit": min(limit, 200),  # ITAD v2 allows up to 200
            "sort": "-cut",  # Sort by discount percentage descending  
            "nondeals": "false",  # Only deals, not regular prices (as string)
            "mature": "false",  # No mature content (as string)
        }

        try:
            # Use the correct endpoint for deals list
            data = await self.http.get_json(f"{self.BASE}/deals/v2", params=params)
            
            deals: List[Deal] = []
            
            # Handle the v2 response structure
            if isinstance(data, dict) and "list" in data:
                deals_data = data["list"]
            else:
                raise ValueError("Unexpected API response format")

            for item in deals_data:
                # Parse deal data from the v2 API structure
                title = self._get_title_v2(item)
                store = self._get_store_v2(item)
                prices = self._get_prices_v2(item)
                discount_pct = self._get_discount_v2(item)
                url = self._get_url_v2(item)

                # Only include deals that meet minimum discount
                if discount_pct and discount_pct >= min_discount:
                    deal: Deal = {
                        "title": title,
                        "price": prices["current"],
                        "store": store,
                        "url": url,
                        "discount": f"{discount_pct}%" if discount_pct else None,
                        "original_price": prices["original"],
                    }
                    deals.append(deal)

            return deals[:limit]  # Ensure we don't exceed requested limit

        except Exception as e:
            # Handle specific API errors
            if hasattr(e, 'status') and e.status == 403:
                raise ValueError("ITAD API key is invalid or expired. Please register your app at https://isthereanydeal.com/apps/my/ to get a valid API key.")
            elif hasattr(e, 'status') and e.status == 404:
                raise ValueError("ITAD API endpoint not found. The API may have changed.")
            else:
                # Re-raise the exception with more context
                raise ValueError(f"ITAD API error: {str(e)}")

    def _get_title_v2(self, item: dict) -> str:
        """Extract title from v2 API structure"""
        return item.get("title", "Unknown Game")

    def _get_store_v2(self, item: dict) -> str:
        """Extract store name from v2 API structure"""
        shop = item.get("shop", {})
        if isinstance(shop, dict):
            return shop.get("name", "Unknown Store")
        return "Unknown Store"

    def _get_prices_v2(self, item: dict) -> dict:
        """Extract current and original prices from v2 API"""
        deal = item.get("deal", {})
        price_new = deal.get("price", {}).get("amount", 0)
        price_old = deal.get("regular", {}).get("amount", 0)
        currency = deal.get("price", {}).get("currency", "USD")
        
        current = f"${price_new:.2f}" if isinstance(price_new, (int, float)) else "Unknown"
        original = f"${price_old:.2f}" if isinstance(price_old, (int, float)) else None
        
        return {"current": current, "original": original}

    def _get_discount_v2(self, item: dict) -> Optional[int]:
        """Extract discount percentage from v2 API"""
        deal = item.get("deal", {})
        discount = deal.get("cut")
        if isinstance(discount, (int, float)):
            return int(discount)
        return None

    def _get_url_v2(self, item: dict) -> str:
        """Extract deal URL from v2 API"""
        deal = item.get("deal", {})
        return deal.get("url", "")