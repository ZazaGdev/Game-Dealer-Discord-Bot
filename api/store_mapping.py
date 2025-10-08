# api/store_mapping.py
"""
Store filtering and shop ID mapping functionality for ITAD API
"""
from typing import Union, Optional, Dict
from models import StoreFilter

class StoreMapper:
    """Handles store name to shop ID mapping and filtering"""
    
    # ITAD shop ID mappings (key = lowercase store name, value = shop ID)
    SHOP_ID_MAP: Dict[str, int] = {
        # Major PC stores
        "steam": 61,
        "epic game store": 16,
        "epic": 16,
        "gog": 35,
        "gog.com": 35,
        
        # Other PC stores
        "humble bundle": 7,
        "humble store": 7,
        "humble": 7,
        "fanatical": 15,
        "green man gaming": 4,
        "gmg": 4,
        "gamesplanet": 17,
        "gamersgate": 8,
        "origin": 13,
        "uplay": 25,
        "ubisoft connect": 25,
        "ubisoft store": 25,
        "battle.net": 37,
        "blizzard": 37,
        "itch.io": 33,
        "itch": 33,
        
        # Console stores  
        "microsoft store": 48,  # Fixed: was incorrectly 47
        "xbox": 48,             # Fixed: was incorrectly 47
        "playstation store": 49,
        "psn": 49,
        "nintendo eshop": 50,
        "nintendo": 50,
    }
    
    # Default stores when no filter is specified (PC-focused)
    DEFAULT_STORES = ["steam", "epic game store", "gog"]
    
    @classmethod
    def get_shop_id(cls, store_name: Union[str, StoreFilter]) -> Optional[int]:
        """
        Convert store name to ITAD shop ID
        
        Args:
            store_name: Store name (case-insensitive)
            
        Returns:
            Shop ID if found, None otherwise
        """
        if not store_name:
            return None
            
        normalized_name = store_name.lower().strip()
        return cls.SHOP_ID_MAP.get(normalized_name)
    
    @classmethod
    def get_default_shop_ids(cls) -> list[int]:
        """Get shop IDs for default stores (Steam, Epic, GOG)"""
        return [cls.get_shop_id(store) for store in cls.DEFAULT_STORES if cls.get_shop_id(store)]
    
    @classmethod
    def matches_store_filter(cls, store_name: str, store_filter: Union[str, StoreFilter]) -> bool:
        """
        Check if a store name matches the given filter
        
        Args:
            store_name: Store name to check
            store_filter: Filter to match against
            
        Returns:
            True if matches, False otherwise
        """
        if not store_filter:
            return True
            
        normalized_store = store_name.lower().strip()
        normalized_filter = store_filter.lower().strip()
        
        # Direct match
        if normalized_store == normalized_filter:
            return True
        
        # Check common aliases
        store_aliases = {
            "epic game store": ["epic", "epic games"],
            "gog.com": ["gog"],
            "humble store": ["humble", "humble bundle"],
            "green man gaming": ["gmg"],
            "ubisoft connect": ["uplay", "ubisoft store"],
            "battle.net": ["blizzard"],
            "microsoft store": ["xbox"],
            "playstation store": ["psn"],
            "nintendo eshop": ["nintendo"]
        }
        
        # Check if filter matches any aliases for this store
        for canonical_name, aliases in store_aliases.items():
            if normalized_store == canonical_name:
                return normalized_filter in aliases or normalized_filter == canonical_name
            elif normalized_store in aliases:
                return normalized_filter == canonical_name or normalized_filter in aliases
        
        return False
    
    @classmethod
    def get_available_stores(cls) -> list[str]:
        """Return a list of all supported store names"""
        # Return canonical names only (not aliases)
        canonical_stores = [
            "Steam", "Epic Game Store", "GOG", "Humble Store", 
            "Fanatical", "Green Man Gaming", "GamesPlanet", 
            "Ubisoft Connect", "Origin", "Microsoft Store",
            "PlayStation Store", "Nintendo eShop", "Battle.net", "itch.io"
        ]
        return canonical_stores