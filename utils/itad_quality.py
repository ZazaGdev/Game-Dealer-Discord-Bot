# utils/itad_quality.py
"""
ITAD Quality Filtering System

Implements quality game detection based on ITAD's approach:
1. Popularity-based filtering using ITAD stats
2. Multi-criteria sorting (popularity, discount, price)
3. Community-driven quality indicators
4. Asset flip detection and filtering
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Set, Tuple
import aiohttp
import asyncio
import logging
from dataclasses import dataclass

@dataclass
class GamePopularityStats:
    """Game popularity statistics from ITAD"""
    game_id: str
    title: str
    rank: Optional[int] = None
    waitlisted_count: int = 0
    collected_count: int = 0
    popularity_score: int = 0  # waitlisted + collected
    
    @property
    def is_popular(self) -> bool:
        """Check if game meets popularity thresholds"""
        return (
            self.waitlisted_count >= 10 or  # At least 10 people want it
            self.collected_count >= 50 or   # At least 50 people own it
            self.popularity_score >= 30     # Combined popularity
        )
    
    @property
    def quality_score(self) -> float:
        """Calculate quality score (0-100) based on popularity"""
        # Base score from popularity
        base_score = min(80, self.popularity_score / 10)
        
        # Bonus for high waitlist (indicates future demand)
        waitlist_bonus = min(10, self.waitlisted_count / 100)
        
        # Bonus for high collection (indicates proven quality)
        collection_bonus = min(10, self.collected_count / 500)
        
        return min(100, base_score + waitlist_bonus + collection_bonus)


class ITADQualityFilter:
    """
    Quality filtering system based on ITAD's approach to showing "interesting games"
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.isthereanydeal.com"
        self._popular_games_cache: Optional[Dict[str, GamePopularityStats]] = None
        self._cache_timestamp: Optional[float] = None
        self.cache_duration = 3600  # 1 hour cache
        
    async def get_popular_games_stats(self, limit: int = 500) -> Dict[str, GamePopularityStats]:
        """
        Fetch popular games from ITAD using their stats endpoints
        Returns dict mapping game titles to popularity stats
        """
        import time
        
        # Return cached data if still valid
        if (self._popular_games_cache and 
            self._cache_timestamp and 
            time.time() - self._cache_timestamp < self.cache_duration):
            return self._popular_games_cache
            
        popular_games: Dict[str, GamePopularityStats] = {}
        
        async with aiohttp.ClientSession() as session:
            # Fetch most waitlisted games
            try:
                waitlisted_url = f"{self.base_url}/stats/most-waitlisted/v1"
                params = {"key": self.api_key, "limit": limit}
                
                async with session.get(waitlisted_url, params=params) as response:
                    if response.status == 200:
                        waitlisted_data = await response.json()
                        for item in waitlisted_data:
                            title = item.get("title", "")
                            if title:
                                popular_games[title.lower()] = GamePopularityStats(
                                    game_id=item.get("id", ""),
                                    title=title,
                                    waitlisted_count=item.get("count", 0),
                                    rank=item.get("position")
                                )
            except Exception as e:
                logging.warning(f"Failed to fetch waitlisted games: {e}")
            
            # Fetch most collected games
            try:
                collected_url = f"{self.base_url}/stats/most-collected/v1"
                params = {"key": self.api_key, "limit": limit}
                
                async with session.get(collected_url, params=params) as response:
                    if response.status == 200:
                        collected_data = await response.json()
                        for item in collected_data:
                            title = item.get("title", "")
                            if title:
                                title_lower = title.lower()
                                if title_lower in popular_games:
                                    # Update existing entry
                                    popular_games[title_lower].collected_count = item.get("count", 0)
                                else:
                                    # Create new entry
                                    popular_games[title_lower] = GamePopularityStats(
                                        game_id=item.get("id", ""),
                                        title=title,
                                        collected_count=item.get("count", 0),
                                        rank=item.get("position")
                                    )
            except Exception as e:
                logging.warning(f"Failed to fetch collected games: {e}")
            
            # Fetch most popular games (combined)
            try:
                popular_url = f"{self.base_url}/stats/most-popular/v1"
                params = {"key": self.api_key, "limit": limit}
                
                async with session.get(popular_url, params=params) as response:
                    if response.status == 200:
                        popular_data = await response.json()
                        for item in popular_data:
                            title = item.get("title", "")
                            if title:
                                title_lower = title.lower()
                                if title_lower in popular_games:
                                    # Update popularity score
                                    popular_games[title_lower].popularity_score = item.get("count", 0)
                                else:
                                    # Create new entry
                                    popular_games[title_lower] = GamePopularityStats(
                                        game_id=item.get("id", ""),
                                        title=title,
                                        popularity_score=item.get("count", 0),
                                        rank=item.get("position")
                                    )
            except Exception as e:
                logging.warning(f"Failed to fetch popular games: {e}")
        
        # Calculate final popularity scores for all games
        for stats in popular_games.values():
            if stats.popularity_score == 0:
                stats.popularity_score = stats.waitlisted_count + stats.collected_count
        
        # Cache the results
        self._popular_games_cache = popular_games
        self._cache_timestamp = time.time()
        
        return popular_games
    
    def is_quality_game(self, title: str, popular_games: Dict[str, GamePopularityStats]) -> Tuple[bool, float]:
        """
        Check if a game meets quality criteria based on ITAD popularity data
        
        Returns:
            Tuple of (is_quality, quality_score)
        """
        title_lower = title.lower()
        
        # Direct match
        if title_lower in popular_games:
            stats = popular_games[title_lower]
            return stats.is_popular, stats.quality_score
        
        # Fuzzy matching for titles with slight variations
        for popular_title, stats in popular_games.items():
            if self._titles_match(title_lower, popular_title):
                return stats.is_popular, stats.quality_score
                
        # Not found in popular games
        return False, 0.0
    
    def _titles_match(self, title1: str, title2: str, threshold: float = 0.8) -> bool:
        """
        Check if two game titles match with fuzzy logic
        """
        # Remove common suffixes/prefixes that might differ
        def normalize_title(title: str) -> str:
            # Remove common variations
            variations_to_remove = [
                " - complete edition", " complete edition", 
                " - definitive edition", " definitive edition",
                " - goty", " goty", " - game of the year",
                " - enhanced edition", " enhanced edition",
                " - director's cut", " director's cut",
                ": enhanced edition", ": definitive edition",
                ": complete edition", ": goty"
            ]
            
            normalized = title.lower().strip()
            for variation in variations_to_remove:
                normalized = normalized.replace(variation, "")
            
            # Remove special characters and extra spaces
            import re
            normalized = re.sub(r'[^\w\s]', ' ', normalized)
            normalized = ' '.join(normalized.split())
            
            return normalized
        
        norm1 = normalize_title(title1)
        norm2 = normalize_title(title2)
        
        # Exact match after normalization
        if norm1 == norm2:
            return True
            
        # Check if one is contained in the other (for subtitles/editions)
        if len(norm1) > 10 and len(norm2) > 10:
            if norm1 in norm2 or norm2 in norm1:
                return True
        
        # Levenshtein distance for small differences
        def levenshtein_ratio(s1: str, s2: str) -> float:
            """Calculate similarity ratio using Levenshtein distance"""
            if not s1 or not s2:
                return 0.0
            
            if s1 == s2:
                return 1.0
                
            len1, len2 = len(s1), len(s2)
            if abs(len1 - len2) > min(len1, len2) * 0.5:  # Too different in length
                return 0.0
            
            # Simple distance calculation
            matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
            
            for i in range(len1 + 1):
                matrix[i][0] = i
            for j in range(len2 + 1):
                matrix[0][j] = j
                
            for i in range(1, len1 + 1):
                for j in range(1, len2 + 1):
                    cost = 0 if s1[i-1] == s2[j-1] else 1
                    matrix[i][j] = min(
                        matrix[i-1][j] + 1,      # deletion
                        matrix[i][j-1] + 1,      # insertion
                        matrix[i-1][j-1] + cost  # substitution
                    )
            
            distance = matrix[len1][len2]
            max_len = max(len1, len2)
            return 1.0 - (distance / max_len) if max_len > 0 else 0.0
        
        similarity = levenshtein_ratio(norm1, norm2)
        return similarity >= threshold
    
    async def get_quality_deals_with_itad_sorting(
        self, 
        api_key: str,
        limit: int = 20,
        min_discount: int = 50,
        sort_by: str = "hottest"  # "hottest", "newest", "price", "cut"
    ) -> List[Dict[str, Any]]:
        """
        Fetch deals using ITAD's quality sorting options
        
        Args:
            sort_by: Sorting method - "hottest" for popular games, "cut" for discount
        """
        # Map our sort options to ITAD API parameters
        sort_mapping = {
            "hottest": "-waitlisted",  # Most waitlisted first (popularity)
            "newest": "-time",         # Newest deals first
            "price": "price",          # Lowest price first  
            "cut": "-cut"              # Highest discount first
        }
        
        sort_param = sort_mapping.get(sort_by, "-cut")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/deals/v2"
            params = {
                "key": api_key,
                "limit": limit,
                "sort": sort_param,
                "nondeals": "false",
                "mature": "false"
            }
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        deals = data.get("list", [])
                        
                        # Filter by discount if specified
                        if min_discount > 0:
                            filtered_deals = []
                            for deal in deals:
                                discount_pct = self._extract_discount_percentage(deal)
                                if discount_pct >= min_discount:
                                    filtered_deals.append(deal)
                            return filtered_deals
                        
                        return deals
                    else:
                        logging.error(f"Failed to fetch deals: HTTP {response.status}")
                        return []
            except Exception as e:
                logging.error(f"Error fetching quality deals: {e}")
                return []
    
    def _extract_discount_percentage(self, deal_item: Dict[str, Any]) -> int:
        """Extract discount percentage from ITAD deal item"""
        try:
            # ITAD v2 API structure
            if "deal" in deal_item and "cut" in deal_item["deal"]:
                return int(deal_item["deal"]["cut"])
            return 0
        except (KeyError, ValueError, TypeError):
            return 0


class EnhancedAssetFlipDetector:
    """
    Enhanced asset flip detection based on multiple quality indicators
    """
    
    # Expanded list of asset flip indicators
    ASSET_FLIP_KEYWORDS = {
        # Generic/low-effort titles
        "simulator", "tycoon", "adventure", "puzzle", "arcade", "casual",
        "indie", "pixel", "retro", "classic", "simple", "easy", "quick",
        
        # Common asset flip patterns
        "zombie", "survival", "battle", "royal", "craft", "mine", "build",
        "farm", "city", "tower", "defense", "endless", "runner", "jump",
        "dash", "rush", "speed", "fast", "super", "mega", "ultra", "hyper",
        
        # Low-effort descriptors
        "fun", "cool", "awesome", "amazing", "best", "ultimate", "extreme",
        "pro", "premium", "deluxe", "special", "edition", "collection",
        
        # Suspicious patterns
        "2d", "3d", "hd", "vr", "ar", "mobile", "android", "ios",
        "free", "cheap", "budget", "low", "poly", "minimal", "basic"
    }
    
    # Red flag title patterns
    SUSPICIOUS_PATTERNS = [
        r"^\w+ \d+$",  # "Word 1", "Game 2"
        r"^\w+ simulator$",  # "X Simulator"
        r"^\w+ tycoon$",  # "X Tycoon"
        r"^\w+ adventure$",  # "X Adventure"
        r"zombie \w+",  # "Zombie X"
        r"\w+ zombie",  # "X Zombie"
        r"battle royale",
        r"survival \w+",
        r"\w+ survival"
    ]
    
    def is_likely_asset_flip(
        self, 
        title: str, 
        price: float, 
        discount_pct: int,
        popularity_stats: Optional[GamePopularityStats] = None
    ) -> bool:
        """
        Enhanced asset flip detection using multiple criteria
        """
        title_lower = title.lower()
        
        # 1. Price-based detection (very cheap games with high discounts)
        if price < 1.0 and discount_pct > 80:
            return True
            
        if price < 0.5:  # Extremely cheap games
            return True
        
        # 2. Title pattern analysis
        import re
        
        # Check suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, title_lower):
                return True
        
        # Count asset flip keywords
        word_count = 0
        keyword_count = 0
        words = title_lower.split()
        
        for word in words:
            word_count += 1
            if word in self.ASSET_FLIP_KEYWORDS:
                keyword_count += 1
        
        # High keyword ratio indicates asset flip
        if word_count > 0 and (keyword_count / word_count) > 0.6:
            return True
        
        # 3. Popularity-based filtering (if available)
        if popularity_stats:
            # Games with very low popularity are likely low quality
            if (popularity_stats.waitlisted_count < 5 and 
                popularity_stats.collected_count < 10 and
                popularity_stats.popularity_score < 10):
                return True
        
        # 4. Title length and complexity
        if len(title) < 5 or len(words) < 2:
            return True  # Too short/simple
        
        # 5. Generic number suffixes
        if re.search(r' \d+$', title_lower) and len(words) <= 3:
            return True  # "Game 2", "Sim 3"
        
        return False