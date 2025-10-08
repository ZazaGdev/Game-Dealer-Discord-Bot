# api/priority_deals.py
"""
Native priority and popularity-based deal fetching for ITAD API
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Literal
import logging
from models import Deal, ITADGameItem
from .http import HttpClient
from .quality_scoring import QualityScorer
from .store_mapping import StoreMapper

PriorityMethod = Literal["hybrid", "popular_deals", "waitlisted_deals", "collected_deals"]

class PriorityDealsClient:
    """Handles priority-based deal fetching using ITAD popularity data"""
    
    def __init__(self, api_key: str, http_client: HttpClient, base_url: str):
        self.api_key = api_key
        self.http = http_client
        self.BASE = base_url
        self.quality_scorer = QualityScorer(api_key, http_client, base_url)
        self.store_mapper = StoreMapper()
    
    async def fetch_native_priority_deals(
        self,
        limit: int = 10,
        min_discount: int = 0,
        priority_method: PriorityMethod = "hybrid",
        store_filter: Optional[str] = None
    ) -> List[Deal]:
        """
        Fetch deals using native ITAD priority methods
        
        Args:
            limit: Maximum number of deals to return
            min_discount: Minimum discount percentage
            priority_method: Method to use ("hybrid", "popular_deals", "waitlisted_deals", "collected_deals")
            store_filter: Store name to filter by (None = default stores)
            
        Returns:
            List of Deal objects
        """
        try:
            logging.info(f"Fetching {priority_method} deals: limit={limit}, min_discount={min_discount}%, store={store_filter}")
            
            # Determine shop IDs
            shop_ids = None
            if store_filter:
                shop_id = self.store_mapper.get_shop_id(store_filter)
                if shop_id:
                    shop_ids = [shop_id]
                    logging.info(f"Using store filter: {store_filter} -> shop ID {shop_id}")
                else:
                    logging.warning(f"Unknown store filter: {store_filter}")
                    return []
            else:
                # Default to Steam, Epic, GOG
                shop_ids = self.store_mapper.get_default_shop_ids()
                logging.info(f"Using default stores -> shop IDs {shop_ids}")
            
            # Route to appropriate method
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
    
    async def _fetch_hybrid_priority_deals(
        self, 
        limit: int, 
        min_discount: int, 
        shop_ids: Optional[List[int]]
    ) -> List[Deal]:
        """
        NEW HYBRID APPROACH: Smart quality-based scoring instead of strict intersection
        
        Strategy:
        1. Get current deals sorted by discount (best deals first)
        2. Score each deal based on multiple quality indicators:
           - Discount percentage (higher = better)
           - Publisher reputation (known good publishers)
           - Title characteristics (avoid obvious shovelware)
           - Review indicators (when available)
           - Historical popularity (loose matching)
        3. Return top-scored deals that provide genuine value
        """
        logging.info("Using improved hybrid approach with quality scoring")
        
        try:
            # Get a large set of current deals for analysis
            deals_params = {
                "key": self.api_key,
                "offset": 0,
                "limit": 200,  # Maximum supported
                "sort": "-cut",  # Sort by discount percentage
                "nondeals": "false",
                "mature": "false"
            }
            
            if shop_ids:
                deals_params["shops"] = ",".join(map(str, shop_ids))
            
            deals_data = await self.http.get_json(f"{self.BASE}/deals/v2", params=deals_params)
            
            if not isinstance(deals_data, dict) or "list" not in deals_data:
                raise ValueError(f"Unexpected deals response: {type(deals_data)}")
            
            # Load popularity data for reference (loose matching)
            popular_games = await self.quality_scorer.load_popularity_reference()
            
            # Score each deal
            scored_deals = []
            
            for deal_item in deals_data["list"]:
                title = self._get_title_v2(deal_item)
                discount_pct = self._get_discount_v2(deal_item)
                
                # Skip deals below minimum discount
                if discount_pct < min_discount:
                    continue
                
                # Calculate quality score
                quality_score = self.quality_scorer.calculate_deal_quality_score(
                    deal_item, title, discount_pct, popular_games
                )
                
                if quality_score > 0:  # Only include deals with positive scores
                    store = self._get_store_v2(deal_item)
                    prices = self._get_prices_v2(deal_item)
                    url = self._get_url_v2(deal_item)
                    
                    deal: Deal = {
                        "title": title,
                        "price": prices["current"],
                        "store": store,
                        "url": url,
                        "discount": f"{discount_pct}%" if discount_pct else None,
                        "original_price": prices["original"]
                    }
                    
                    scored_deals.append({
                        "deal": deal,
                        "quality_score": quality_score,
                        "discount_pct": discount_pct
                    })
            
            # Sort by quality score (highest first)
            scored_deals.sort(key=lambda x: x["quality_score"], reverse=True)
            
            # Return top deals
            result_deals = [item["deal"] for item in scored_deals[:limit]]
            
            logging.info(f"Hybrid approach found {len(result_deals)} quality deals from {len(scored_deals)} candidates")
            return result_deals
            
        except Exception as e:
            logging.error(f"Error in hybrid priority deals: {e}")
            # Fallback to simple discount-sorted deals
            return await self._fetch_fallback_deals(limit, min_discount, shop_ids)
    
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
                    if self.quality_scorer._titles_match_fuzzy(title_lower, popular_title):
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
        
        # Clean up metadata and convert to Deal objects
        final_deals: List[Deal] = []
        for deal_dict in matched_deals[:limit]:
            # Remove internal fields and create proper Deal object
            clean_deal: Deal = {
                "title": deal_dict["title"],
                "price": deal_dict["price"],
                "store": deal_dict["store"],
                "url": deal_dict["url"],
                "discount": deal_dict.get("discount"),
                "original_price": deal_dict.get("original_price")
            }
            final_deals.append(clean_deal)
        
        logging.info(f"Found {len(final_deals)} popular {popularity_type} deals from {len(matched_deals)} total matches")
        
        # If we found very few matches, expand the search to include more games
        if len(final_deals) < limit // 2:  # If we got less than half requested
            logging.info(f"Low intersection results ({len(final_deals)}), expanding search with relaxed criteria")
            additional_deals = await self._fetch_expanded_popularity_deals(
                limit - len(final_deals),
                min_discount,
                shop_ids,
                popularity_type,
                exclude_titles=[deal["title"] for deal in final_deals]
            )
            final_deals.extend(additional_deals)
        
        return final_deals
    
    async def _fetch_expanded_popularity_deals(
        self,
        limit: int,
        min_discount: int,
        shop_ids: Optional[List[int]],
        popularity_type: str,
        exclude_titles: List[str]
    ) -> List[Deal]:
        """
        Fallback method when strict intersection yields few results.
        Uses relaxed criteria to find more deals.
        
        Strategy:
        1. Get popular games from a larger set (top 1000)
        2. Use multiple matching techniques (fuzzy, partial, keyword)
        3. Include high-discount deals from quality publishers
        4. Apply quality scoring to filter out shovelware
        """
        logging.info(f"Expanding {popularity_type} search with relaxed criteria")
        
        try:
            # Get a much larger set of popular games
            if popularity_type == "popular":
                endpoint = f"{self.BASE}/stats/most-popular/v1"
            elif popularity_type == "waitlisted":
                endpoint = f"{self.BASE}/stats/most-waitlisted/v1"
            elif popularity_type == "collected":
                endpoint = f"{self.BASE}/stats/most-collected/v1"
            else:
                # Fallback to popular for unknown types
                endpoint = f"{self.BASE}/stats/most-popular/v1"
            
            # Get larger set of popular games
            params = {
                "key": self.api_key,
                "limit": 1000,  # Much larger set
                "offset": 0
            }
            
            popular_data = await self.http.get_json(endpoint, params=params)
            
            # Build comprehensive lookup including keywords
            popular_lookup = {}
            popular_keywords = set()
            
            for item in popular_data:
                title = item.get("title", "").lower()
                if title and title not in [t.lower() for t in exclude_titles]:
                    popular_lookup[title] = {
                        "title": item.get("title", ""),
                        "count": item.get("count", 0),
                        "position": item.get("position", 999),
                        "popularity_score": max(0, 1000 - item.get("position", 999))
                    }
                    
                    # Extract keywords from popular titles
                    words = title.replace("'", "").split()
                    for word in words:
                        if len(word) > 3 and word not in {'game', 'edition', 'collection', 'remastered'}:
                            popular_keywords.add(word)
            
            # Get current deals with larger limit
            deals_params = {
                "key": self.api_key,
                "offset": 0,
                "limit": 200,  # Get more deals (max supported)
                "sort": "-cut",  # Sort by discount
                "nondeals": "false",
                "mature": "false"
            }
            
            if shop_ids:
                deals_params["shops"] = ",".join(map(str, shop_ids))
            
            deals_data = await self.http.get_json(f"{self.BASE}/deals/v2", params=deals_params)
            
            if not isinstance(deals_data, dict) or "list" not in deals_data:
                return []
            
            expanded_matches = []
            exclude_titles_lower = [t.lower() for t in exclude_titles]
            
            for deal_item in deals_data["list"]:
                title = self._get_title_v2(deal_item)
                title_lower = title.lower()
                
                # Skip already included titles
                if title_lower in exclude_titles_lower:
                    continue
                
                discount_pct = self._get_discount_v2(deal_item)
                if discount_pct < min_discount:
                    continue
                
                match_score = 0
                popularity_info = None
                
                # Direct match (highest priority)
                if title_lower in popular_lookup:
                    popularity_info = popular_lookup[title_lower]
                    match_score = 100
                
                # Fuzzy matching for close variants
                elif not popularity_info:
                    for pop_title, info in popular_lookup.items():
                        if self.quality_scorer._titles_match_fuzzy(title_lower, pop_title):
                            popularity_info = info
                            match_score = 80
                            break
                
                # Keyword matching for broader relevance
                elif not popularity_info and discount_pct >= 50:  # High discount threshold
                    title_words = set(title_lower.replace("'", "").split())
                    keyword_matches = title_words.intersection(popular_keywords)
                    
                    if len(keyword_matches) >= 2:  # At least 2 keyword matches
                        # Create synthetic popularity info for keyword matches
                        popularity_info = {
                            "title": title,
                            "count": 100,  # Low synthetic count
                            "position": 900,  # Low priority position
                            "popularity_score": 100  # Low score
                        }
                        match_score = 40
                
                if popularity_info and match_score > 0:
                    store = self._get_store_v2(deal_item)
                    prices = self._get_prices_v2(deal_item)
                    url = self._get_url_v2(deal_item)
                    
                    deal: Deal = {
                        "title": title,
                        "price": prices["current"],
                        "store": store,
                        "url": url,
                        "discount": f"{discount_pct}%" if discount_pct else None,
                        "original_price": prices["original"]
                    }
                    
                    expanded_matches.append({
                        "deal": deal,
                        "match_score": match_score,
                        "popularity_score": popularity_info["popularity_score"],
                        "discount_pct": discount_pct
                    })
            
            # Sort by combined score (match quality + popularity + discount)
            expanded_matches.sort(
                key=lambda x: (
                    x["match_score"],
                    x["popularity_score"],
                    x["discount_pct"]
                ),
                reverse=True
            )
            
            # Return top deals
            result_deals = [match["deal"] for match in expanded_matches[:limit]]
            logging.info(f"Expanded search found {len(result_deals)} additional deals")
            
            return result_deals
            
        except Exception as e:
            logging.error(f"Error in expanded popularity search: {e}")
            return []
    
    async def _fetch_fallback_deals(
        self,
        limit: int,
        min_discount: int,
        shop_ids: Optional[List[int]]
    ) -> List[Deal]:
        """Simple fallback that returns highest discount deals"""
        try:
            deals_params = {
                "key": self.api_key,
                "offset": 0,
                "limit": limit,
                "sort": "-cut",
                "nondeals": "false",
                "mature": "false"
            }
            
            if shop_ids:
                deals_params["shops"] = ",".join(map(str, shop_ids))
            
            deals_data = await self.http.get_json(f"{self.BASE}/deals/v2", params=deals_params)
            
            if not isinstance(deals_data, dict) or "list" not in deals_data:
                return []
            
            fallback_deals = []
            for deal_item in deals_data["list"]:
                discount_pct = self._get_discount_v2(deal_item)
                if discount_pct >= min_discount:
                    title = self._get_title_v2(deal_item)
                    store = self._get_store_v2(deal_item)
                    prices = self._get_prices_v2(deal_item)
                    url = self._get_url_v2(deal_item)
                    
                    deal: Deal = {
                        "title": title,
                        "price": prices["current"],
                        "store": store,
                        "url": url,
                        "discount": f"{discount_pct}%" if discount_pct else None,
                        "original_price": prices["original"]
                    }
                    
                    fallback_deals.append(deal)
            
            return fallback_deals
            
        except Exception as e:
            logging.error(f"Error in fallback deals: {e}")
            return []
    
    # Helper methods for parsing deal data (duplicated from main client for now)
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