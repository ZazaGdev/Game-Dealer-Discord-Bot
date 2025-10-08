# api/quality_scoring.py
"""
Quality scoring and hybrid priority approaches for ITAD deals
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
import logging
from models import Deal, ITADGameItem
from .http import HttpClient

class QualityScorer:
    """Handles quality-based scoring for deals"""
    
    def __init__(self, api_key: str, http_client: HttpClient, base_url: str):
        self.api_key = api_key
        self.http = http_client
        self.BASE = base_url
    
    def calculate_deal_quality_score(
        self, 
        deal_item: dict, 
        title: str, 
        discount_pct: int,
        popular_games: dict
    ) -> float:
        """
        Calculate quality score for a deal based on multiple factors
        Score components:
        - Discount bonus: 0-40 points (higher discount = more points)
        - Popularity bonus: 0-30 points (known popular games get bonus)
        - Publisher quality: 0-20 points (reputable publishers get bonus)  
        - Title quality: -10 to +10 points (avoid obvious shovelware)
        """
        score = 0.0
        title_lower = title.lower()
        
        # 1. Discount Score (0-40 points)
        # More aggressive scoring for higher discounts
        if discount_pct >= 90:
            score += 40
        elif discount_pct >= 80:
            score += 35
        elif discount_pct >= 70:
            score += 30
        elif discount_pct >= 60:
            score += 25
        elif discount_pct >= 50:
            score += 20
        elif discount_pct >= 30:
            score += 15
        else:
            score += discount_pct * 0.3  # Proportional for smaller discounts
        
        # 2. Popularity Bonus (0-30 points)
        popularity_bonus = 0
        
        # Direct match
        if title_lower in popular_games:
            position = popular_games[title_lower]["position"]
            if position <= 50:
                popularity_bonus = 30
            elif position <= 100:
                popularity_bonus = 25
            elif position <= 200:
                popularity_bonus = 20
            elif position <= 500:
                popularity_bonus = 15
            else:
                popularity_bonus = 10
        else:
            # Fuzzy matching for variants
            for pop_title, info in popular_games.items():
                if self._titles_match_fuzzy(title_lower, pop_title):
                    position = info["position"]
                    # Reduced bonus for fuzzy matches
                    if position <= 100:
                        popularity_bonus = 15
                    elif position <= 300:
                        popularity_bonus = 10
                    else:
                        popularity_bonus = 5
                    break
        
        score += popularity_bonus
        
        # 3. Publisher/Quality Indicators (0-20 points)
        quality_indicators = [
            # Known quality publishers/franchises (partial matching)
            'valve', 'nintendo', 'sony', 'microsoft', 'blizzard', 'rockstar',
            'bethesda', 'ubisoft', 'ea', 'activision', 'square enix', 'capcom',
            'fromsoftware', 'cd projekt', 'larian', 'obsidian', 'insomniac',
            # Quality franchise keywords
            'call of duty', 'assassin', 'final fantasy', 'grand theft', 'elder scrolls',
            'fallout', 'bioshock', 'borderlands', 'civilization', 'total war',
            'resident evil', 'street fighter', 'mortal kombat', 'tekken',
            'dark souls', 'sekiro', 'bloodborne', 'witcher', 'cyberpunk',
            # Well-reviewed indie keywords
            'stardew', 'terraria', 'hollow knight', 'celeste', 'hades',
            'cuphead', 'ori and', 'steamworld', 'shovel knight', 'undertale'
        ]
        
        quality_bonus = 0
        for indicator in quality_indicators:
            if indicator in title_lower:
                quality_bonus = 20
                break
        
        score += quality_bonus
        
        # 4. Negative Quality Indicators (-10 points for shovelware signs)
        shovelware_indicators = [
            # Common shovelware patterns
            'hentai', 'anime girl', 'waifu', 'strip', 'adult only',
            'quick ', 'simple ', 'easy ', 'basic ', 'mini ',
            'volume', 'pack', 'bundle', 'collection',
            # Asset flip indicators
            'livingforest', 'gamemaker', 'unity asset',
            # Low-effort patterns  
            'simulator 20', 'tycoon 20', 'manager 20',
            'vr chat', 'vrchat', 'metaverse'
        ]
        
        for indicator in shovelware_indicators:
            if indicator in title_lower:
                score -= 10
                break
        
        return max(0, score)  # Never return negative scores
    
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
    
    async def load_popularity_reference(self) -> dict:
        """Load popularity data for loose reference matching"""
        try:
            # Get a large set from multiple popularity sources
            all_popular = {}
            
            for endpoint_type in ["most-popular", "most-waitlisted", "most-collected"]:
                params = {
                    "key": self.api_key,
                    "limit": 500,  # Large set for comprehensive reference
                    "offset": 0
                }
                
                endpoint = f"{self.BASE}/stats/{endpoint_type}/v1"
                data = await self.http.get_json(endpoint, params=params)
                
                for item in data:
                    title = item.get("title", "").lower()
                    if title:
                        # Use highest position if already exists
                        existing_pos = all_popular.get(title, {}).get("position", 999)
                        new_pos = item.get("position", 999)
                        
                        if new_pos < existing_pos:  # Better position
                            all_popular[title] = {
                                "title": item.get("title", ""),
                                "position": new_pos,
                                "count": item.get("count", 0),
                                "type": endpoint_type
                            }
            
            logging.info(f"Loaded {len(all_popular)} games for popularity reference")
            return all_popular
            
        except Exception as e:
            logging.error(f"Error loading popularity reference: {e}")
            return {}