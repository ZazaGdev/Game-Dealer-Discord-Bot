# models/models.py
from typing import TypedDict, Optional, Literal, Union
from datetime import datetime

# Store filtering types
StoreFilter = Literal[
    "Steam", "Epic Game Store", "Epic", "GOG", "GOG.com", "Fanatical", 
    "Humble Store", "Humble", "Green Man Gaming", "GMG", "Origin", 
    "Uplay", "Ubisoft Connect", "Microsoft Store", "Xbox", 
    "PlayStation Store", "PSN", "Nintendo eShop", "Nintendo", 
    "Battle.net", "Blizzard", "itch.io", "itch"
]

# Basic deal data structure
class Deal(TypedDict, total=False):
    title: str
    price: str
    store: str
    url: str
    discount: Optional[str]
    original_price: Optional[str]

# Enhanced deal with metadata (for future use)
class EnhancedDeal(Deal, total=False):
    fetched_at: datetime
    shop_id: int
    discount_percentage: Optional[int]  # Numeric discount for sorting
    price_numeric: Optional[float]      # Numeric price for comparison
    currency: str

# API response metadata
class APIResponse(TypedDict, total=False):
    total_items: int
    has_more: bool
    next_offset: Optional[int]
    endpoint: str
    timestamp: datetime

# Configuration types
class BotConfig(TypedDict):
    discord_token: str
    log_channel_id: int
    deals_channel_id: int
    itad_api_key: str
    debug_api_responses: bool
