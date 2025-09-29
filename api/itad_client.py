# api/itad_client.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
from .http import HttpClient
from models import Deal
from utils.game_filters import PriorityGameFilter

class ITADClient:
    BASE = "https://api.isthereanydeal.com"

    def __init__(self, api_key: Optional[str] = None, http: Optional[HttpClient] = None):
        headers = {}
        self.http = http or HttpClient(headers=headers)
        self.api_key = api_key
        self.priority_filter = PriorityGameFilter()

    async def close(self) -> None:
        await self.http.close()

    async def fetch_deals(self, *, min_discount: int = 60, limit: int = 10, store_filter: str = None, 
                         log_full_response: bool = False, quality_filter: bool = True, 
                         min_priority: int = 5) -> List[Deal]:
        """
        Fetch deals using the correct ITAD API endpoints with priority-based filtering
        
        Args:
            min_discount: Minimum discount percentage (default: 60)
            limit: Maximum number of deals to return (default: 10)
            store_filter: Filter by specific store name (e.g. "Steam", "Epic Game Store") 
            log_full_response: Whether to log full API response to api_responses.json
            quality_filter: Whether to filter for priority games only (default: True)
            min_priority: Minimum priority score for games (1-10, default: 5)
        """
        if not self.api_key:
            raise ValueError("ITAD API key is required")

        # Convert store name to shop ID if store_filter is provided
        shop_ids = None
        if store_filter:
            shop_id = self._get_shop_id(store_filter)
            if shop_id:
                shop_ids = [shop_id]
            else:
                # If store not found, return empty list rather than error
                return []

        # Use the correct ITAD API endpoint - deals/v2
        # Fetch more deals when quality filtering is enabled to ensure we have enough after strict filtering
        api_limit = limit
        if quality_filter:
            # Request significantly more deals since we're now doing strict priority filtering
            # If we need N deals after filtering, request up to 15x more to account for strict filtering
            api_limit = min(limit * 15, 200)  # ITAD v2 allows up to 200
        
        params: Dict[str, Any] = {
            "key": self.api_key,
            "offset": 0,
            "limit": api_limit,
            "sort": "-cut",  # Sort by discount percentage descending  
            "nondeals": "false",  # Only deals, not regular prices (as string)
            "mature": "false",  # No mature content (as string)
        }
        
        # Add shop filter if specified
        if shop_ids:
            params["shops"] = ",".join(map(str, shop_ids))

        try:
            # Use the correct endpoint for deals list
            data = await self.http.get_json(f"{self.BASE}/deals/v2", params=params)
            
            # Check if the API returned an error response
            if isinstance(data, dict) and "error" in data:
                error_details = data.get("error", {})
                if isinstance(error_details, dict):
                    error_message = error_details.get("message", "Unknown API error")
                else:
                    error_message = str(error_details)
                raise ValueError(f"ITAD API returned error: {error_message}")
            
            # Log full API responses when requested (typically from Discord commands)
            if log_full_response:
                await self._log_full_api_response(data, params, store_filter)
            
            # Optional: Log API responses for debugging (controlled by environment variable)
            import os
            if os.getenv("DEBUG_API_RESPONSES", "false").lower() == "true":
                import json
                log_dir = "logs"
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                with open(f"{log_dir}/api_responses.json", "a", encoding="utf-8") as f:
                    timestamp = __import__("datetime").datetime.now().isoformat()
                    log_entry = {
                        "timestamp": timestamp,
                        "endpoint": "/deals/v2",
                        "params": {k: v for k, v in params.items() if k != "key"},  # Don't log API key
                        "response_summary": {
                            "items_count": len(data.get("list", [])) if isinstance(data, dict) else 0,
                            "has_more": data.get("hasMore", False) if isinstance(data, dict) else False
                        }
                    }
                    f.write(json.dumps(log_entry, indent=2) + "\n---\n")
            
            deals: List[Deal] = []
            
            # Handle the v2 response structure with better error reporting
            if isinstance(data, dict) and "list" in data:
                deals_data = data["list"]
            else:
                # Log what we actually received for debugging
                import json
                response_preview = json.dumps(data, indent=2)[:500] if data else "None"
                error_msg = f"Unexpected API response format. Expected dict with 'list' key, got: {type(data).__name__}"
                if isinstance(data, dict):
                    error_msg += f" with keys: {list(data.keys())}"
                error_msg += f". Response preview: {response_preview}"
                raise ValueError(error_msg)

            # First, collect all qualifying deals (discount threshold)
            all_deals = []
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
                    all_deals.append(deal)

            # Apply priority filtering if enabled - STRICT MODE ONLY
            if quality_filter:
                deals = self.priority_filter.filter_deals_by_priority(
                    all_deals, 
                    min_priority=min_priority,
                    max_results=limit,
                    strict_mode=True  # Only return games that match the priority database
                )
                
                # If we don't have enough deals after strict filtering, try to get more
                if len(deals) < limit and len(all_deals) > len(deals):
                    # Try with a lower priority threshold to get more results
                    if min_priority > 1:
                        additional_deals = self.priority_filter.filter_deals_by_priority(
                            all_deals,
                            min_priority=max(1, min_priority - 2),  # Lower threshold
                            max_results=limit,
                            strict_mode=True
                        )
                        
                        # If we got more deals with lower threshold, use those
                        if len(additional_deals) > len(deals):
                            deals = additional_deals
            else:
                deals = all_deals[:limit]  # Just limit without filtering

            return deals

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
        # Based on actual API response: store is in item["deal"]["shop"]["name"]
        deal = item.get("deal", {})
        if isinstance(deal, dict):
            shop = deal.get("shop", {})
            if isinstance(shop, dict):
                store_name = shop.get("name")
                if store_name:
                    return str(store_name)
        
        # Fallback: try direct shop object (older structure or different endpoint)
        shop = item.get("shop", {})
        if isinstance(shop, dict):
            store_name = shop.get("name") or shop.get("title") or shop.get("id")
            if store_name:
                return str(store_name)
        
        # Last resort fallbacks
        if "store" in item:
            return str(item["store"])
        
        return "Unknown Store"

    def _get_prices_v2(self, item: dict) -> dict:
        """Extract current and original prices from v2 API"""
        deal = item.get("deal", {})
        
        # Get current price
        price_data = deal.get("price", {})
        price_new = price_data.get("amount", 0)
        currency = price_data.get("currency", "USD")
        
        # Get regular/original price
        regular_data = deal.get("regular", {})
        price_old = regular_data.get("amount", 0)
        
        # Format prices
        if currency == "USD":
            current = f"${price_new:.2f}" if isinstance(price_new, (int, float)) else "Free" if price_new == 0 else "Unknown"
            original = f"${price_old:.2f}" if isinstance(price_old, (int, float)) and price_old > 0 else None
        else:
            current = f"{price_new:.2f} {currency}" if isinstance(price_new, (int, float)) else "Free" if price_new == 0 else "Unknown"
            original = f"{price_old:.2f} {currency}" if isinstance(price_old, (int, float)) and price_old > 0 else None
        
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
    
    def _matches_store_filter(self, store_name: str, store_filter: str) -> bool:
        """Check if store name matches the filter (case-insensitive partial match)"""
        return store_filter.lower() in store_name.lower()
    
    def _get_shop_id(self, store_name: str) -> Optional[int]:
        """
        Convert store name to shop ID based on ITAD API mappings
        
        Args:
            store_name: Store name (case-insensitive)
            
        Returns:
            Shop ID if found, None otherwise
        """
        # Mapping of store names to shop IDs (from ITAD API /service/shops/v1)
        store_mappings = {
            "steam": 61,
            "epic game store": 16,
            "epic": 16,  # Common abbreviation
            "gog": 35,
            "gog.com": 35,
            "fanatical": 6,
            "humble store": 37,
            "humble": 37,  # Common abbreviation
            "green man gaming": 36,
            "gmg": 36,  # Common abbreviation
            "origin": 4,
            "uplay": 1,
            "ubisoft connect": 1,  # Updated name
            "microsoft store": 47,
            "xbox": 47,  # Common association
            "playstation store": 43,
            "psn": 43,  # Common abbreviation
            "nintendo eshop": 49,
            "nintendo": 49,  # Common abbreviation
            "battle.net": 2,
            "blizzard": 2,  # Common association
            "itch.io": 11,
            "itch": 11,  # Common abbreviation
            "direct2drive": 7,
            "gamersgate": 9,
            "indiegala": 13,
            "chrono.gg": 44,
            "chrono": 44,  # Common abbreviation
            "wingamestore": 14,
            "dlgamer": 15,
            "nuuvem": 12,
            "gamefly": 10,
            "g2a": 8,
            "kinguin": 20,
            "cdkeys": 21,
            "2game": 22,
            "gamivo": 23,
            "eneba": 46,
        }
        
        # Normalize store name for lookup
        normalized_name = store_name.lower().strip()
        return store_mappings.get(normalized_name)

    async def _log_full_api_response(self, data: Dict, params: Dict, store_filter: str = None) -> None:
        """Log full API response to api_responses.json for Discord command analysis"""
        try:
            import json
            import os
            from datetime import datetime
            
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Create detailed log entry with full response data
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "source": "discord_command",
                "endpoint": "/deals/v2",
                "request_params": {k: v for k, v in params.items() if k != "key"},  # Don't log API key
                "store_filter": store_filter,
                "response_summary": {
                    "total_items": len(data.get("list", [])) if isinstance(data, dict) else 0,
                    "has_more": data.get("hasMore", False) if isinstance(data, dict) else False,
                    "next_offset": data.get("nextOffset") if isinstance(data, dict) else None
                },
                "first_5_deals": data.get("list", [])[:5] if isinstance(data, dict) else []  # Store only first 5 for space
            }
            
            api_log_file = f"{log_dir}/api_responses.json"
            
            # Read existing entries if file exists
            existing_entries = []
            if os.path.exists(api_log_file):
                try:
                    with open(api_log_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            existing_entries = json.loads(content) if content.startswith('[') else [json.loads(content)]
                except (json.JSONDecodeError, FileNotFoundError):
                    existing_entries = []
            
            # Add new entry
            existing_entries.append(log_entry)
            
            # Keep only last 50 entries to prevent file from growing too large
            if len(existing_entries) > 50:
                existing_entries = existing_entries[-50:]
            
            # Write back to file
            with open(api_log_file, "w", encoding="utf-8") as f:
                json.dump(existing_entries, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            # Don't let logging errors affect the main functionality
            print(f"Warning: Failed to log API response: {e}")
    
    def get_available_stores(self) -> list:
        """Return a list of common store names for filtering"""
        return [
            "Steam", "Epic Game Store", "GOG", "Humble Bundle", 
            "Fanatical", "Green Man Gaming", "GamesPlanet", 
            "Ubisoft Store", "Origin", "Microsoft Store",
            "PlayStation Store", "Nintendo eShop"
        ]