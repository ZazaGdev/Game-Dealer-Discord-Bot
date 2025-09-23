# utils/game_filters.py
"""
Quality game filtering utilities for GameDealer bot.
Helps filter out courses, tutorials, and non-game content to focus on actual games.
"""
import re
from typing import List, Dict, Any, Optional

class GameQualityFilter:
    """Filters deals to focus on quality games rather than courses or non-game content"""
    
    # Quality stores that primarily sell games (not courses/software)
    QUALITY_GAME_STORES = {
        61: "Steam",              # Primary game platform
        35: "GOG",                # DRM-free games  
        16: "Epic Game Store",    # Major game platform
        2: "GamesPlanet",         # Game focused
        7: "Humble Store",        # Game bundles (though they sell courses too)
        25: "Gamesload",          # Game retailer
        3: "GreenManGaming",      # Game focused
        1: "Direct2Drive",        # Game downloads
        4: "GamersGate",          # Game retailer
        37: "Nintendo eShop",     # Console games
        68: "Microsoft Store",    # Console + PC games
    }
    
    # Keywords that strongly indicate non-game content
    NON_GAME_KEYWORDS = [
        # Educational content
        'course', 'tutorial', 'learn', 'training', 'education',
        'masterclass', 'bootcamp', 'certification', 'study',
        'lesson', 'workshop', 'seminar', 'class',
        
        # Programming/technical content
        'python', 'javascript', 'programming', 'coding', 'development',
        'web dev', 'software dev', 'data science', 'machine learning',
        'unity tutorial', 'unreal tutorial', 'blender course',
        
        # Software/tools (not games)
        'software', 'tool', 'plugin', 'asset pack', 'template',
        'photoshop', 'adobe', 'office', 'productivity',
        
        # Business/professional content
        'business', 'marketing', 'finance', 'accounting',
        'project management', 'leadership', 'productivity'
    ]
    
    # Patterns that indicate non-game content
    NON_GAME_PATTERNS = [
        r'\bhow\s+to\b',                          # "How to..."
        r'\blearn\s+\w+\s+in\s+\d+',             # "Learn Python in 30"
        r'\b\d+\s+(courses?|tutorials?)\b',      # "5 Courses", "10 Tutorials"
        r'\bcomplete\s+\w+\s+course\b',          # "Complete Python Course"
        r'\bfrom\s+zero\s+to\s+hero\b',         # "From Zero to Hero"
        r'\bstep\s+by\s+step\b',                 # "Step by Step"
        r'\bbeginners?\s+guide\b',               # "Beginners Guide"
        r'\bmasterclass\s+in\b',                 # "Masterclass in..."
        r'\bcertification\s+prep\b',             # "Certification Prep"
        r'\b\d+\s+hours?\s+of\b',                # "20 Hours of..."
    ]
    
    # Store IDs that often sell courses/non-game content (use with caution)
    MIXED_CONTENT_STORES = {
        6: "Fanatical",  # Sells both games and courses
        7: "Humble",     # Humble Bundle - mixed content
    }

    @classmethod
    def is_quality_game(cls, title: str, store_name: str = "", store_id: int = None) -> bool:
        """
        Determine if this appears to be a quality game worth showing
        
        Args:
            title: Game/item title
            store_name: Store name (optional)
            store_id: Store ID (optional)
            
        Returns:
            True if this appears to be a quality game
        """
        # Filter 1: Remove obvious non-game content by title keywords
        if cls._contains_non_game_keywords(title):
            return False
        
        # Filter 2: Remove items matching non-game patterns
        if cls._matches_non_game_patterns(title):
            return False
            
        # Filter 3: Title length - very short titles often aren't games
        if len(title.strip()) < 3:
            return False
            
        # Filter 4: Store-based filtering (if store info available)
        if store_id and cls._is_quality_game_store(store_id):
            # If it's from a quality game store, more likely to be a game
            return True
        elif store_id and store_id in cls.MIXED_CONTENT_STORES:
            # Mixed content stores need stricter filtering
            return cls._passes_strict_filtering(title)
        
        # Default: assume it's a game if it passes other filters
        return True
    
    @classmethod
    def _contains_non_game_keywords(cls, title: str) -> bool:
        """Check if title contains keywords indicating non-game content"""
        title_lower = title.lower()
        
        for keyword in cls.NON_GAME_KEYWORDS:
            if keyword in title_lower:
                return True
        
        return False
    
    @classmethod
    def _matches_non_game_patterns(cls, title: str) -> bool:
        """Check if title matches patterns indicating non-game content"""
        title_lower = title.lower()
        
        for pattern in cls.NON_GAME_PATTERNS:
            if re.search(pattern, title_lower):
                return True
                
        return False
    
    @classmethod
    def _is_quality_game_store(cls, store_id: int) -> bool:
        """Check if store primarily sells quality games"""
        return store_id in cls.QUALITY_GAME_STORES
    
    @classmethod
    def _passes_strict_filtering(cls, title: str) -> bool:
        """Apply stricter filtering for mixed-content stores"""
        title_lower = title.lower()
        
        # Additional strict patterns for mixed stores
        strict_patterns = [
            r'\bundefined\b',                     # Often placeholder content
            r'\b(mega|ultimate|complete)\s+pack\b',  # Often course bundles
            r'\b\w+\s+(bundle|collection)\s+\d+\b', # "Course Bundle 5"
            r'\bultimate\s+\w+\s+bundle\b',      # "Ultimate Learning Bundle"
        ]
        
        for pattern in strict_patterns:
            if re.search(pattern, title_lower):
                return False
                
        return True
    
    @classmethod
    def filter_deals(cls, deals: List[Dict[str, Any]], apply_store_filter: bool = True) -> List[Dict[str, Any]]:
        """
        Filter a list of deals to keep only quality games
        
        Args:
            deals: List of deal dictionaries
            apply_store_filter: Whether to apply store-based filtering
            
        Returns:
            Filtered list of quality game deals
        """
        quality_deals = []
        
        for deal in deals:
            title = deal.get('title', '')
            store_name = deal.get('store', '')
            store_id = deal.get('store_id')  # If available in deal data
            
            if cls.is_quality_game(title, store_name, store_id):
                quality_deals.append(deal)
        
        return quality_deals
    
    @classmethod
    def get_quality_store_ids(cls) -> List[int]:
        """Get list of store IDs that primarily sell quality games"""
        return list(cls.QUALITY_GAME_STORES.keys())
    
    @classmethod
    def get_store_name_by_id(cls, store_id: int) -> Optional[str]:
        """Get store name by ID from quality stores mapping"""
        return cls.QUALITY_GAME_STORES.get(store_id)


# Convenience functions for direct use
def is_quality_game(title: str, store_name: str = "", store_id: int = None) -> bool:
    """Convenience function to check if an item is a quality game"""
    return GameQualityFilter.is_quality_game(title, store_name, store_id)

def filter_quality_games(deals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function to filter deals for quality games"""
    return GameQualityFilter.filter_deals(deals)

def get_quality_store_ids() -> List[int]:
    """Convenience function to get quality store IDs"""
    return GameQualityFilter.get_quality_store_ids()