# api/itad_client.py
"""
Refactored ITAD Client - Core functionality only
Dependencies split into focused modules:
- store_mapping.py: Store filtering and shop ID mapping
- priority_deals.py: Native priority and popularity methods
- quality_scoring.py: Quality scoring and hybrid approaches
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Union, Tuple, Literal
import aiohttp
import logging
import os
from .http import HttpClient
from models import Deal, ITADGameItem, StoreFilter, APIError
from utils.game_filters import PriorityGameFilter
from utils.itad_quality import ITADQualityFilter, EnhancedAssetFlipDetector
from .store_mapping import StoreMapper
from .priority_deals import PriorityDealsClient, PriorityMethod

class ITADClient:
    """Client for IsThereAnyDeal API with type safety and error handling"""
    BASE: str = "https://api.isthereanydeal.com"

    def __init__(self, api_key: Optional[str] = None, http: Optional[HttpClient] = None) -> None:
        headers = {}
        self.http = http or HttpClient(headers=headers)
        self.api_key = api_key
        self.priority_filter = PriorityGameFilter()
        
        # Initialize quality filtering system
        self.quality_filter = ITADQualityFilter(api_key) if api_key else None
        self.asset_flip_detector = EnhancedAssetFlipDetector()
        
        # Initialize sub-clients
        self.store_mapper = StoreMapper()
        if api_key:
            self.priority_client = PriorityDealsClient(api_key, self.http, self.BASE)
        else:
            self.priority_client = None

    async def close(self) -> None:
        await self.http.close()

    async def fetch_deals(
        self, 
        *, 
        min_discount: int = 60, 
        limit: int = 10, 
        store_filter: Optional[Union[str, StoreFilter]] = None, 
        log_full_response: bool = False, 
        quality_filter: bool = True, 
        min_priority: int = 5
    ) -> List[Deal]:
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
        
        logging.info(f"Fetching deals: discount>={min_discount}%, limit={limit}, store={store_filter}")
        
        try:
            # Step 1: Get shop IDs from store filter
            shop_ids = None
            if store_filter:
                shop_id = self.store_mapper.get_shop_id(store_filter)
                if shop_id:
                    shop_ids = [shop_id]
                    logging.info(f"Store filter '{store_filter}' mapped to shop ID: {shop_id}")
                else:
                    logging.warning(f"Unknown store filter: {store_filter}")
                    return []
            else:
                # Default to Steam, Epic, GOG when no store specified
                shop_ids = self.store_mapper.get_default_shop_ids()
                logging.info(f"No store filter specified, using default stores: {shop_ids}")
            
            # Step 2: Fetch deals from ITAD API
            params = {
                "key": self.api_key,
                "offset": 0,
                "limit": limit,
                "sort": "-cut",  # Sort by discount percentage
                "nondeals": "false",
                "mature": "false"
            }
            
            if shop_ids:
                params["shops"] = ",".join(map(str, shop_ids))
            
            logging.info(f"API request params: {params}")
            data = await self.http.get_json(f"{self.BASE}/deals/v2", params=params)
            
            if not isinstance(data, dict) or "list" not in data:
                raise ValueError(f"Unexpected API response structure: {type(data)}")
            
            # Log full response if requested
            if log_full_response:
                await self._log_full_api_response(data, params, store_filter)
            
            # Step 3: Process deals
            deals = []
            for item in data["list"]:
                try:
                    # Extract deal information
                    title = self._get_title_v2(item)
                    discount_pct = self._get_discount_v2(item)
                    
                    # Apply discount filter
                    if discount_pct is None or discount_pct < min_discount:
                        continue
                    
                    # Apply store filter (double-check)
                    store = self._get_store_v2(item)
                    if store_filter and not self.store_mapper.matches_store_filter(store, store_filter):
                        continue
                    
                    # Apply quality filter if enabled
                    if quality_filter and not self._passes_quality_filter(item, title, min_priority):
                        continue
                    
                    # Extract other deal data
                    prices = self._get_prices_v2(item)
                    url = self._get_url_v2(item)
                    
                    deal: Deal = {
                        "title": title,
                        "price": prices["current"],
                        "store": store,
                        "url": url,
                        "discount": f"{discount_pct}%" if discount_pct else None,
                        "original_price": prices["original"]
                    }
                    
                    deals.append(deal)
                    
                except Exception as e:
                    logging.warning(f"Failed to process deal item: {e}")
                    continue
            
            logging.info(f"Processed {len(deals)} deals from {len(data['list'])} API results")
            return deals
            
        except Exception as e:
            logging.error(f"Failed to fetch deals: {e}")
            raise APIError(f"Failed to fetch deals: {e}")

    async def fetch_quality_deals_itad_method(
        self, 
        *, 
        limit: int = 10, 
        min_discount: int = 60, 
        store_filter: Optional[Union[str, StoreFilter]] = None,
        log_full_response: bool = False
    ) -> List[Deal]:
        """
        Fetch quality deals using ITAD's built-in quality system
        """
        if not self.api_key:
            raise ValueError("ITAD API key is required")
        
        logging.info(f"Fetching quality deals: discount>={min_discount}%, limit={limit}, store={store_filter}")
        
        try:
            # Get shop IDs
            shop_ids = None
            if store_filter:
                shop_id = self.store_mapper.get_shop_id(store_filter)
                if shop_id:
                    shop_ids = [shop_id]
                else:
                    logging.warning(f"Unknown store filter: {store_filter}")
                    return []
            else:
                # Default to Steam, Epic, GOG
                shop_ids = self.store_mapper.get_default_shop_ids()
            
            # Use quality API endpoint if available, otherwise fall back to regular deals
            params = {
                "key": self.api_key,
                "offset": 0,
                "limit": limit,
                "sort": "-cut",
                "nondeals": "false",
                "mature": "false"
            }
            
            if shop_ids:
                params["shops"] = ",".join(map(str, shop_ids))
            
            # Try quality-enhanced endpoint first
            try:
                data = await self.http.get_json(f"{self.BASE}/deals/v2", params=params)
            except Exception:
                # Fallback to regular deals endpoint
                data = await self.http.get_json(f"{self.BASE}/deals/v2", params=params)
            
            if not isinstance(data, dict) or "list" not in data:
                raise ValueError(f"Unexpected API response: {type(data)}")
            
            # Log full response if requested
            if log_full_response:
                await self._log_full_api_response(data, params, store_filter)
            
            # Process deals with enhanced quality filtering
            quality_deals = []
            for item in data["list"]:
                try:
                    title = self._get_title_v2(item)
                    discount_pct = self._get_discount_v2(item)
                    
                    # Apply discount filter
                    if discount_pct is None or discount_pct < min_discount:
                        continue
                    
                    # Apply store filter
                    store = self._get_store_v2(item)
                    if store_filter and not self.store_mapper.matches_store_filter(store, store_filter):
                        continue
                    
                    # Enhanced quality filtering using ITAD quality system
                    if self.quality_filter and not self.quality_filter.is_quality_game(title):
                        continue
                    
                    # Asset flip detection
                    if self.asset_flip_detector.is_likely_asset_flip(title, store):
                        logging.debug(f"Filtered out potential asset flip: {title}")
                        continue
                    
                    prices = self._get_prices_v2(item)
                    url = self._get_url_v2(item)
                    
                    deal: Deal = {
                        "title": title,
                        "price": prices["current"],
                        "store": store,
                        "url": url,
                        "discount": f"{discount_pct}%" if discount_pct else None,
                        "original_price": prices["original"]
                    }
                    
                    quality_deals.append(deal)
                    
                except Exception as e:
                    logging.warning(f"Failed to process quality deal: {e}")
                    continue
            
            logging.info(f"Found {len(quality_deals)} quality deals from {len(data.get('list', []))} total")
            return quality_deals
            
        except Exception as e:
            logging.error(f"Failed to fetch quality deals: {e}")
            raise APIError(f"Failed to fetch quality deals: {e}")

    async def fetch_native_priority_deals(
        self,
        limit: int = 10,
        min_discount: int = 0,
        priority_method: PriorityMethod = "hybrid",
        store_filter: Optional[str] = None
    ) -> List[Deal]:
        """
        Delegate to PriorityDealsClient for native priority functionality
        """
        if not self.priority_client:
            raise ValueError("ITAD API key is required for priority deals")
        
        return await self.priority_client.fetch_native_priority_deals(
            limit=limit,
            min_discount=min_discount,
            priority_method=priority_method,
            store_filter=store_filter
        )

    # Helper methods for parsing deal data
    def _get_title_v2(self, item: ITADGameItem) -> str:
        return item.get("title", "Unknown Game")

    def _get_store_v2(self, item: ITADGameItem) -> str:
        shop_info = item.get("deal", {}).get("shop", {})
        if isinstance(shop_info, dict):
            shop_name = shop_info.get("name", "Unknown Store")
            # Convert known internal names to display names
            display_names = {
                "Steam": "Steam",
                "Epic Games Store": "Epic Game Store", 
                "GOG": "GOG",
                "Humble Store": "Humble Store",
                "Fanatical": "Fanatical",
                "Green Man Gaming": "Green Man Gaming",
                "GamesPlanet": "GamesPlanet",
                "Ubisoft Store": "Ubisoft Store",
                "Origin": "Origin",
                "Battle.net": "Battle.net",
                "Microsoft Store": "Microsoft Store",
                "PlayStation Store": "PlayStation Store",
                "Nintendo eShop": "Nintendo eShop",
            }
            return display_names.get(shop_name, shop_name)
        return "Unknown Store"

    def _get_prices_v2(self, item: ITADGameItem) -> Dict[str, str]:
        deal_info = item.get("deal", {})
        
        # Current discounted price
        current_price = deal_info.get("price", {})
        if isinstance(current_price, dict):
            current_amount = current_price.get("amount", 0)
            current_formatted = f"${current_amount:.2f}" if current_amount else "Free"
        else:
            current_formatted = "Unknown"
        
        # Original price
        regular_price = deal_info.get("regular", {})
        if isinstance(regular_price, dict):
            regular_amount = regular_price.get("amount", 0)
            original_formatted = f"${regular_amount:.2f}" if regular_amount else "Free"
        else:
            original_formatted = current_formatted  # Fallback
        
        return {
            "current": current_formatted,
            "original": original_formatted
        }

    def _get_discount_v2(self, item: ITADGameItem) -> Optional[int]:
        deal_info = item.get("deal", {})
        discount = deal_info.get("cut")
        return discount if isinstance(discount, int) else None

    def _get_url_v2(self, item: ITADGameItem) -> str:
        deal_info = item.get("deal", {})
        return deal_info.get("url", "")

    def _passes_quality_filter(self, item: ITADGameItem, title: str, min_priority: int) -> bool:
        """Check if a deal passes quality filtering"""
        if not self.priority_filter:
            return True
        
        # Check priority game filter
        if self.priority_filter.has_priority_games():
            priority_info = self.priority_filter.get_game_priority(title)
            if priority_info and priority_info.get("priority", 0) >= min_priority:
                return True
            elif priority_info:  # Game is in list but below threshold
                return False
            # If game not in priority list, continue with other filters
        
        # Additional quality checks
        if self.quality_filter:
            return self.quality_filter.is_quality_game(title)
        
        return True

    async def _log_full_api_response(self, data: Dict[str, Any], params: Dict[str, Any], store_filter: Optional[str] = None) -> None:
        """Log full API response to file for debugging"""
        try:
            log_entry = {
                "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None)),
                "params": params,
                "store_filter": store_filter,
                "response_summary": {
                    "total_items": len(data.get("list", [])),
                    "has_more": data.get("has_more", False),
                    "sample_titles": [item.get("title", "Unknown") for item in data.get("list", [])[:5]]
                },
                "full_response": data
            }
            
            # Ensure logs directory exists
            logs_dir = "logs"
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            # Append to log file
            import json
            log_file = os.path.join(logs_dir, "api_responses.json")
            with open(log_file, "a", encoding="utf-8") as f:
                json.dump(log_entry, f, indent=2, ensure_ascii=False)
                f.write("\n" + "="*50 + "\n")
            
            logging.info(f"Full API response logged to {log_file}")
            
        except Exception as e:
            logging.warning(f"Failed to log API response: {e}")

    def get_available_stores(self) -> list[str]:
        """Return a list of available store names for filtering"""
        return self.store_mapper.get_available_stores()