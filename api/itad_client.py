# api/itad_client.py
from __future__ import annotations
from typing import List, Dict, Any, Optional, Union, Tuple, Literal
import aiohttp
import logging
import os
from .http import HttpClient
from models import Deal, ITADGameItem, StoreFilter, APIError
from utils.game_filters import PriorityGameFilter
from utils.itad_quality import ITADQualityFilter, EnhancedAssetFlipDetector

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

        # Convert store name to shop ID if store_filter is provided
        shop_ids: Optional[List[int]] = None
        if store_filter:
            shop_id: Optional[int] = self._get_shop_id(store_filter)
            if shop_id:
                shop_ids = [shop_id]
            else:
                # If store not found, return empty list rather than error
                return []

        # Use the correct ITAD API endpoint - deals/v2
        # Fetch more deals when quality filtering is enabled to ensure we have enough after strict filtering
        # Also fetch more deals to account for asset flip filtering
        api_limit = limit
        if quality_filter:
            # Request significantly more deals since we're now doing strict priority + asset flip filtering
            # If we need N deals after filtering, request up to 25x more to account for filtering
            api_limit = min(limit * 25, 200)  # ITAD v2 allows up to 200
        else:
            # Even without quality filter, fetch more to account for asset flip filtering
            api_limit = min(limit * 5, 200)
        
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

            # First, collect all qualifying deals (discount threshold + asset flip filtering)
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
                    # Filter out obvious asset flip games to improve quality
                    current_price = 0
                    try:
                        # Extract numeric price for asset flip detection
                        price_str = prices["current"].replace("$", "").replace(",", "")
                        current_price = float(price_str)
                    except (ValueError, AttributeError):
                        pass
                    
                    # Skip obvious asset flip games
                    from utils.game_filters import GameQualityFilter
                    quality_filter_obj = GameQualityFilter()
                    if quality_filter_obj.is_asset_flip(title, current_price, discount_pct):
                        continue  # Skip this asset flip game
                    
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
                
                # If we don't have enough deals after strict filtering, try to get more from API
                if len(deals) < limit and data.get("hasMore", False):
                    # Make additional API requests with higher offsets to find more quality games
                    additional_offset = api_limit
                    max_additional_requests = 3
                    
                    for request_num in range(max_additional_requests):
                        if len(deals) >= limit:
                            break
                            
                        # Request more deals with offset
                        additional_params = params.copy()
                        additional_params["offset"] = additional_offset
                        additional_params["limit"] = api_limit
                        
                        additional_data = await self.http.get_json(f"{self.BASE}/deals/v2", params=additional_params)
                        
                        if "list" in additional_data:
                            additional_deals = []
                            for item in additional_data["list"]:
                                title = self._get_title_v2(item)
                                store = self._get_store_v2(item)
                                prices = self._get_prices_v2(item)
                                discount_pct = self._get_discount_v2(item)
                                url = self._get_url_v2(item)

                                if discount_pct and discount_pct >= min_discount:
                                    current_price = 0
                                    try:
                                        price_str = prices["current"].replace("$", "").replace(",", "")
                                        current_price = float(price_str)
                                    except (ValueError, AttributeError):
                                        pass
                                    
                                    # Skip asset flip games
                                    from utils.game_filters import GameQualityFilter
                                    quality_filter_obj = GameQualityFilter()
                                    if quality_filter_obj.is_asset_flip(title, current_price, discount_pct):
                                        continue
                                    
                                    deal: Deal = {
                                        "title": title,
                                        "price": prices["current"],
                                        "store": store,
                                        "url": url,
                                        "discount": f"{discount_pct}%" if discount_pct else None,
                                        "original_price": prices["original"],
                                    }
                                    additional_deals.append(deal)
                            
                            # Filter additional deals by priority
                            additional_priority_deals = self.priority_filter.filter_deals_by_priority(
                                additional_deals,
                                min_priority=min_priority,
                                max_results=limit - len(deals),
                                strict_mode=True
                            )
                            
                            deals.extend(additional_priority_deals)
                            additional_offset += api_limit
                        
                        if not additional_data.get("hasMore", False):
                            break
                
                # If still not enough, try with lower priority threshold
                if len(deals) < limit and min_priority > 1:
                    lower_priority_deals = self.priority_filter.filter_deals_by_priority(
                        all_deals,
                        min_priority=max(1, min_priority - 2),
                        max_results=limit,
                        strict_mode=True
                    )
                    
                    if len(lower_priority_deals) > len(deals):
                        deals = lower_priority_deals
            else:
                deals = all_deals[:limit]  # Just limit without filtering

            return deals

        except aiohttp.ClientResponseError as e:
            # Handle specific HTTP errors with better messages
            if e.status == 403:
                raise ValueError("ITAD API key is invalid or expired. Please register your app at https://isthereanydeal.com/apps/my/ to get a valid API key.")
            elif e.status == 404:
                raise ValueError("ITAD API endpoint not found. The API may have changed.")
            elif e.status >= 500:
                # Server errors - more user-friendly messages
                if e.status == 502:
                    raise ValueError("ITAD API service is temporarily unavailable (Bad Gateway). Please try again later.")
                elif e.status == 503:
                    raise ValueError("ITAD API service is temporarily unavailable (Service Unavailable). Please try again later.")
                elif e.status == 504:
                    raise ValueError("ITAD API request timed out (Gateway Timeout). Please try again later.")
                else:
                    raise ValueError(f"ITAD API server error (HTTP {e.status}). Please try again later.")
            else:
                raise ValueError(f"ITAD API client error: HTTP {e.status}")
        except ValueError as e:
            # API response format issues
            if "Unexpected API response format" in str(e):
                raise ValueError(f"ITAD API returned invalid data format. This may be due to a temporary service issue. Please try again later.")
            else:
                raise
        except Exception as e:
            # General network or other errors
            raise ValueError(f"ITAD API error: {str(e)}")

    def _get_title_v2(self, item: ITADGameItem) -> str:
        """Extract title from v2 API structure"""
        return item.get("title", "Unknown Game")

    def _get_store_v2(self, item: ITADGameItem) -> str:
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

    def _get_prices_v2(self, item: ITADGameItem) -> Dict[str, str]:
        """Extract current and original prices from v2 API"""
        deal = item.get("deal", {})
        
        # Get current price
        price_data = deal.get("price", {})
        price_new: float = price_data.get("amount", 0.0)
        currency: str = price_data.get("currency", "USD")
        
        # Get regular/original price
        regular_data = deal.get("regular", {})
        price_old: float = regular_data.get("amount", 0.0)
        
        # Format prices
        if currency == "USD":
            current = f"${price_new:.2f}" if isinstance(price_new, (int, float)) else "Free" if price_new == 0 else "Unknown"
            original = f"${price_old:.2f}" if isinstance(price_old, (int, float)) and price_old > 0 else None
        else:
            current = f"{price_new:.2f} {currency}" if isinstance(price_new, (int, float)) else "Free" if price_new == 0 else "Unknown"
            original = f"{price_old:.2f} {currency}" if isinstance(price_old, (int, float)) and price_old > 0 else None
        
        return {"current": current, "original": original}

    def _get_discount_v2(self, item: ITADGameItem) -> Optional[int]:
        """Extract discount percentage from v2 API"""
        deal = item.get("deal", {})
        discount: Any = deal.get("cut")
        if isinstance(discount, (int, float)):
            return int(discount)
        return None

    def _get_url_v2(self, item: ITADGameItem) -> str:
        """Extract deal URL from v2 API"""
        deal = item.get("deal", {})
        return deal.get("url", "")
    
    def _matches_store_filter(self, store_name: str, store_filter: Union[str, StoreFilter]) -> bool:
        """Check if store name matches the filter (case-insensitive partial match)"""
        return str(store_filter).lower() in store_name.lower()
    
    def _get_shop_id(self, store_name: Union[str, StoreFilter]) -> Optional[int]:
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

    async def _log_full_api_response(self, data: Dict[str, Any], params: Dict[str, Any], store_filter: Optional[str] = None) -> None:
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
    
    async def fetch_quality_deals_itad_method(
        self,
        *,
        limit: int = 10,
        min_discount: int = 50,
        sort_by: str = "hottest",  # "hottest", "newest", "price", "cut"
        store_filter: Optional[Union[str, StoreFilter]] = None,
        use_popularity_stats: bool = True
    ) -> List[Deal]:
        """
        Fetch quality deals using ITAD's own approach for showing "interesting games"
        
        This method replicates how ITAD website shows quality games by:
        1. Using ITAD's sorting options (hottest = most popular)
        2. Leveraging community popularity stats (waitlisted/collected counts)
        3. Enhanced asset flip detection
        4. Multi-criteria quality scoring
        
        Args:
            limit: Number of deals to return
            min_discount: Minimum discount percentage
            sort_by: ITAD sorting method ("hottest" for popular games)
            store_filter: Optional store filter
            use_popularity_stats: Whether to use ITAD popularity data for quality scoring
        """
        if not self.api_key:
            raise ValueError("ITAD API key is required")
            
        if not self.quality_filter:
            raise ValueError("Quality filter not initialized - API key required")
        
        # Convert store filter to shop IDs
        shop_ids: Optional[List[int]] = None
        if store_filter:
            shop_id = self._get_shop_id(store_filter)
            if shop_id:
                shop_ids = [shop_id]
            else:
                return []
        
        # Fetch popular games stats if requested
        popular_games = {}
        if use_popularity_stats:
            try:
                popular_games = await self.quality_filter.get_popular_games_stats(limit=500)
                logging.info(f"Loaded popularity stats for {len(popular_games)} games")
            except Exception as e:
                logging.warning(f"Failed to load popularity stats: {e}")
        
        # Map sort options to ITAD API parameters
        sort_mapping = {
            "hottest": "-waitlisted",  # Most waitlisted (popular) games first
            "popular": "-waitlisted",  # Alias for hottest
            "newest": "-time",         # Newest deals first
            "price": "price",          # Lowest price first
            "discount": "-cut",        # Highest discount first
            "cut": "-cut"              # Alias for discount
        }
        
        sort_param = sort_mapping.get(sort_by, "-cut")
        
        # Request more deals to account for quality filtering
        api_limit = min(limit * 10, 200)  # Request 10x more for quality filtering
        
        params: Dict[str, Any] = {
            "key": self.api_key,
            "offset": 0,
            "limit": api_limit,
            "sort": sort_param,
            "nondeals": "false",
            "mature": "false"
        }
        
        # Add shop filter if specified
        if shop_ids:
            params["shops"] = ",".join(map(str, shop_ids))
        
        try:
            data = await self.http.get_json(f"{self.BASE}/deals/v2", params=params)
            
            if isinstance(data, dict) and "error" in data:
                error_details = data.get("error", {})
                error_message = error_details.get("message", "Unknown API error") if isinstance(error_details, dict) else str(error_details)
                raise ValueError(f"ITAD API returned error: {error_message}")
            
            deals: List[Deal] = []
            
            if not isinstance(data, dict) or "list" not in data:
                raise ValueError(f"Unexpected API response format: {type(data).__name__}")
            
            deals_data = data["list"]
            quality_deals = []
            
            for item in deals_data:
                title = self._get_title_v2(item)
                store = self._get_store_v2(item)
                prices = self._get_prices_v2(item)
                discount_pct = self._get_discount_v2(item)
                url = self._get_url_v2(item)
                
                # Apply minimum discount filter
                if discount_pct and discount_pct >= min_discount:
                    # Extract price for asset flip detection
                    current_price = 0
                    try:
                        price_str = prices["current"].replace("$", "").replace(",", "")
                        current_price = float(price_str)
                    except (ValueError, AttributeError):
                        pass
                    
                    # Get popularity stats for this game
                    popularity_stats = None
                    if use_popularity_stats and popular_games:
                        is_quality, quality_score = self.quality_filter.is_quality_game(title, popular_games)
                        if is_quality:
                            # Find the exact stats for enhanced asset flip detection
                            title_lower = title.lower()
                            if title_lower in popular_games:
                                popularity_stats = popular_games[title_lower]
                    
                    # Enhanced asset flip detection
                    is_asset_flip = self.asset_flip_detector.is_likely_asset_flip(
                        title, current_price, discount_pct, popularity_stats
                    )
                    
                    # Only include high-quality games
                    if not is_asset_flip:
                        # Calculate quality score
                        quality_score = 0
                        if popularity_stats:
                            quality_score = popularity_stats.quality_score
                        elif not use_popularity_stats:
                            # Base quality score without popularity data
                            quality_score = 50  # Neutral score
                        
                        deal: Deal = {
                            "title": title,
                            "price": prices["current"], 
                            "store": store,
                            "url": url,
                            "discount": f"{discount_pct}%" if discount_pct else None,
                            "original_price": prices["original"],
                        }
                        
                        # Add quality score for sorting
                        deal["_quality_score"] = quality_score
                        quality_deals.append(deal)
            
            # Sort deals by quality score (highest first), then by discount
            quality_deals.sort(
                key=lambda x: (x.get("_quality_score", 0), 
                             int(x.get("discount", "0%").replace("%", "")) if x.get("discount") else 0),
                reverse=True
            )
            
            # Remove quality score from final results and limit
            final_deals = []
            for deal in quality_deals[:limit]:
                if "_quality_score" in deal:
                    del deal["_quality_score"]
                final_deals.append(deal)
            
            logging.info(f"ITAD Quality Method: Found {len(final_deals)} quality games from {len(deals_data)} total deals")
            return final_deals
            
        except Exception as e:
            logging.error(f"Failed to fetch quality deals using ITAD method: {e}")
            raise
    
    async def fetch_native_priority_deals(
        self,
        *,
        limit: int = 10,
        min_discount: int = 30,
        store_filter: Optional[Union[str, StoreFilter]] = None,
        priority_method: str = "popular_deals"  # "popular_deals", "waitlisted_deals", "collected_deals", "hybrid"
    ) -> List[Deal]:
        """
        Fetch priority deals using native ITAD API approaches without local JSON database
        
        This method uses ITAD's own popularity data and advanced deals/v2 parameters to find
        the most interesting and popular games currently on sale.
        
        Methods:
        - popular_deals: Uses most-popular endpoint + deals intersection
        - waitlisted_deals: Uses most-waitlisted endpoint + deals intersection  
        - collected_deals: Uses most-collected endpoint + deals intersection
        - hybrid: Combines multiple approaches for best results
        
        Args:
            limit: Number of deals to return
            min_discount: Minimum discount percentage
            store_filter: Optional store filter
            priority_method: Method to determine priority games
        """
        if not self.api_key:
            raise ValueError("ITAD API key is required")
        
        # Convert store filter to shop IDs
        shop_ids: Optional[List[int]] = None
        if store_filter:
            shop_id = self._get_shop_id(store_filter)
            if shop_id:
                shop_ids = [shop_id]
            else:
                return []
        
        try:
            if priority_method == "hybrid":
                return await self._fetch_hybrid_priority_deals(limit, min_discount, shop_ids)
            elif priority_method == "popular_deals":
                return await self._fetch_popular_intersection_deals(limit, min_discount, shop_ids, "popular")
            elif priority_method == "waitlisted_deals":
                return await self._fetch_popular_intersection_deals(limit, min_discount, shop_ids, "waitlisted")
            elif priority_method == "collected_deals":
                return await self._fetch_popular_intersection_deals(limit, min_discount, shop_ids, "collected")
            else:
                raise ValueError(f"Unknown priority method: {priority_method}")
                
        except Exception as e:
            logging.error(f"Failed to fetch native priority deals: {e}")
            raise

    async def _fetch_popular_intersection_deals(
        self, 
        limit: int, 
        min_discount: int, 
        shop_ids: Optional[List[int]], 
        popularity_type: str
    ) -> List[Deal]:
        """
        Fetch deals by intersecting popular games with current deals
        
        Strategy:
        1. Get popular games from ITAD stats endpoints
        2. Get current deals from deals/v2 with optimized parameters
        3. Find intersection of popular games that are currently on sale
        4. Rank by popularity score and discount
        """
        # Step 1: Get popular games IDs and titles
        popular_games_data = {}
        
        if popularity_type == "popular":
            endpoint = f"{self.BASE}/stats/most-popular/v1"
        elif popularity_type == "waitlisted":
            endpoint = f"{self.BASE}/stats/most-waitlisted/v1"
        elif popularity_type == "collected":
            endpoint = f"{self.BASE}/stats/most-collected/v1"
        else:
            raise ValueError(f"Unknown popularity type: {popularity_type}")
        
        # Fetch popular games (get more to improve intersection chances)
        params = {
            "key": self.api_key,
            "limit": 500,  # Get top 500 popular games
            "offset": 0
        }
        
        popular_data = await self.http.get_json(endpoint, params=params)
        
        # Build lookup for popular games with their scores
        for item in popular_data:
            game_id = item.get("id")
            title = item.get("title", "").lower()
            slug = item.get("slug", "")
            count = item.get("count", 0)
            position = item.get("position", 999)
            
            if title and (game_id or slug):
                popular_games_data[title] = {
                    "id": game_id,
                    "title": item.get("title", ""),
                    "slug": slug,
                    "count": count,
                    "position": position,
                    "popularity_score": max(0, 600 - position)  # Higher position = higher score
                }
        
        logging.info(f"Loaded {len(popular_games_data)} {popularity_type} games from ITAD")
        
        # Step 2: Get current deals with optimized parameters
        deals_params = {
            "key": self.api_key,
            "offset": 0,
            "limit": 200,  # Get many deals for better intersection
            "sort": "-cut",  # Sort by discount for good deals
            "nondeals": "false",
            "mature": "false"
        }
        
        # Add shop filter if specified
        if shop_ids:
            deals_params["shops"] = ",".join(map(str, shop_ids))
        
        deals_data = await self.http.get_json(f"{self.BASE}/deals/v2", params=deals_params)
        
        if not isinstance(deals_data, dict) or "list" not in deals_data:
            raise ValueError(f"Unexpected deals API response: {type(deals_data)}")
        
        # Step 3: Find intersection - deals for popular games
        matched_deals = []
        
        for deal_item in deals_data["list"]:
            title = self._get_title_v2(deal_item)
            discount_pct = self._get_discount_v2(deal_item)
            
            # Check minimum discount
            if discount_pct < min_discount:
                continue
            
            title_lower = title.lower()
            
            # Check if this deal is for a popular game
            popularity_info = None
            
            # Direct title match
            if title_lower in popular_games_data:
                popularity_info = popular_games_data[title_lower]
            else:
                # Fuzzy title matching for variations
                for popular_title, info in popular_games_data.items():
                    if self._titles_match_fuzzy(title_lower, popular_title):
                        popularity_info = info
                        break
            
            if popularity_info:
                # This is a deal for a popular game!
                store = self._get_store_v2(deal_item)
                prices = self._get_prices_v2(deal_item)
                url = self._get_url_v2(deal_item)
                
                deal: Deal = {
                    "title": title,
                    "price": prices["current"],
                    "store": store,
                    "url": url,
                    "discount": f"{discount_pct}%" if discount_pct else None,
                    "original_price": prices["original"],
                }
                
                # Add popularity metadata for sorting
                deal["_popularity_score"] = popularity_info["popularity_score"]
                deal["_popularity_count"] = popularity_info["count"]
                deal["_popularity_position"] = popularity_info["position"]
                
                matched_deals.append(deal)
        
        # Step 4: Rank by popularity and discount
        matched_deals.sort(
            key=lambda x: (
                x.get("_popularity_score", 0),  # Primary: popularity
                int(x.get("discount", "0%").replace("%", "")) if x.get("discount") else 0,  # Secondary: discount
                -x.get("_popularity_position", 999)  # Tertiary: position (lower is better)
            ),
            reverse=True
        )
        
        # Clean up metadata and return
        final_deals = []
        for deal in matched_deals[:limit]:
            # Remove internal fields
            for key in list(deal.keys()):
                if key.startswith("_"):
                    del deal[key]
            final_deals.append(deal)
        
        logging.info(f"Found {len(final_deals)} popular {popularity_type} deals from {len(matched_deals)} total matches")
        return final_deals

    async def _fetch_hybrid_priority_deals(
        self, 
        limit: int, 
        min_discount: int, 
        shop_ids: Optional[List[int]]
    ) -> List[Deal]:
        """
        Hybrid approach combining multiple ITAD popularity sources for best results
        
        Strategy:
        1. Get deals from most-popular (40% weight)
        2. Get deals from most-waitlisted (35% weight) 
        3. Get deals from most-collected (25% weight)
        4. Combine and deduplicate with weighted scoring
        """
        # Fetch from all three popularity sources
        popular_deals = await self._fetch_popular_intersection_deals(
            limit * 2, min_discount, shop_ids, "popular"
        )
        
        waitlisted_deals = await self._fetch_popular_intersection_deals(
            limit * 2, min_discount, shop_ids, "waitlisted"
        )
        
        collected_deals = await self._fetch_popular_intersection_deals(
            limit * 2, min_discount, shop_ids, "collected"
        )
        
        # Combine with weighted scoring
        combined_deals = {}
        
        # Add popular deals (40% weight)
        for i, deal in enumerate(popular_deals):
            title_key = deal["title"].lower()
            score = (len(popular_deals) - i) * 0.4
            combined_deals[title_key] = {
                "deal": deal,
                "score": score,
                "sources": ["popular"]
            }
        
        # Add waitlisted deals (35% weight)  
        for i, deal in enumerate(waitlisted_deals):
            title_key = deal["title"].lower()
            score = (len(waitlisted_deals) - i) * 0.35
            
            if title_key in combined_deals:
                combined_deals[title_key]["score"] += score
                combined_deals[title_key]["sources"].append("waitlisted")
            else:
                combined_deals[title_key] = {
                    "deal": deal,
                    "score": score,
                    "sources": ["waitlisted"]
                }
        
        # Add collected deals (25% weight)
        for i, deal in enumerate(collected_deals):
            title_key = deal["title"].lower()
            score = (len(collected_deals) - i) * 0.25
            
            if title_key in combined_deals:
                combined_deals[title_key]["score"] += score
                combined_deals[title_key]["sources"].append("collected")
            else:
                combined_deals[title_key] = {
                    "deal": deal,
                    "score": score,
                    "sources": ["collected"]
                }
        
        # Sort by combined score and return top deals
        sorted_deals = sorted(
            combined_deals.values(),
            key=lambda x: (x["score"], len(x["sources"])),  # Score first, then source diversity
            reverse=True
        )
        
        final_deals = [item["deal"] for item in sorted_deals[:limit]]
        
        logging.info(f"Hybrid method combined {len(combined_deals)} unique games, returning top {len(final_deals)}")
        return final_deals

    def _titles_match_fuzzy(self, title1: str, title2: str) -> bool:
        """
        Fuzzy title matching for game variations
        """
        # Quick exact match
        if title1 == title2:
            return True
        
        # Remove common variations and normalize
        def normalize_title(title: str) -> str:
            # Remove edition suffixes
            editions = [
                " complete edition", " definitive edition", " goty", 
                " enhanced edition", " director's cut", " remastered",
                " game of the year", " ultimate edition", " deluxe edition"
            ]
            
            normalized = title.lower().strip()
            for edition in editions:
                normalized = normalized.replace(edition, "")
            
            # Remove punctuation and extra spaces
            import re
            normalized = re.sub(r'[^\w\s]', ' ', normalized)
            normalized = ' '.join(normalized.split())
            
            return normalized
        
        norm1 = normalize_title(title1)
        norm2 = normalize_title(title2)
        
        # Check normalized match
        if norm1 == norm2:
            return True
        
        # Check substring match for longer titles
        if len(norm1) > 8 and len(norm2) > 8:
            shorter = norm1 if len(norm1) < len(norm2) else norm2
            longer = norm1 if len(norm1) >= len(norm2) else norm2
            
            if shorter in longer:
                return True
        
        return False

    def get_available_stores(self) -> list:
        """Return a list of common store names for filtering"""
        return [
            "Steam", "Epic Game Store", "GOG", "Humble Bundle", 
            "Fanatical", "Green Man Gaming", "GamesPlanet", 
            "Ubisoft Store", "Origin", "Microsoft Store",
            "PlayStation Store", "Nintendo eShop"
        ]