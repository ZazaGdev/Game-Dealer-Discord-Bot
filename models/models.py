# models/models.py
from typing import TypedDict, Optional, Literal, Union, Protocol, Any, Dict, List, runtime_checkable
from datetime import datetime

# Store filtering types
StoreFilter = Literal[
    "Steam", "Epic Game Store", "Epic", "GOG", "GOG.com", "Fanatical", 
    "Humble Store", "Humble", "Green Man Gaming", "GMG", "Origin", 
    "Uplay", "Ubisoft Connect", "Microsoft Store", "Xbox", 
    "PlayStation Store", "PSN", "Nintendo eShop", "Nintendo", 
    "Battle.net", "Blizzard", "itch.io", "itch"
]

# Priority game data structure
class PriorityGame(TypedDict):
    title: str
    priority: int  # 1-10 scale
    category: str
    notes: str

# ITAD API response structures
class ITADShop(TypedDict):
    id: int
    name: str

class ITADPrice(TypedDict):
    amount: float
    amountInt: int
    currency: str

class ITADDealData(TypedDict, total=False):
    shop: ITADShop
    price: ITADPrice
    regular: ITADPrice
    cut: int  # Discount percentage
    voucher: Optional[str]
    storeLow: Optional[ITADPrice]
    historyLow: Optional[ITADPrice]
    flag: Optional[str]
    drm: List[Dict[str, Any]]
    platforms: List[str]
    timestamp: str
    expiry: Optional[str]
    url: str

class ITADGameAssets(TypedDict, total=False):
    boxart: Optional[str]
    banner145: Optional[str]
    banner300: Optional[str]
    banner400: Optional[str]
    banner600: Optional[str]

class ITADGameItem(TypedDict, total=False):
    id: str
    slug: str
    title: str
    type: Optional[str]
    mature: bool
    assets: ITADGameAssets
    deal: ITADDealData

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

# Protocol interfaces for better type safety
@runtime_checkable
class InteractionLike(Protocol):
    """Protocol for Discord interaction-like objects"""
    async def response_send_message(self, content: str, *, ephemeral: bool = False) -> None: ...
    async def edit_original_response(self, *, content: Optional[str] = None, embed: Optional[Any] = None) -> None: ...
    async def followup_send(self, *, content: Optional[str] = None, embed: Optional[Any] = None) -> None: ...
    @property
    def response(self) -> Any: ...
    @property
    def followup(self) -> Any: ...

@runtime_checkable 
class ContextLike(Protocol):
    """Protocol for Discord context-like objects"""
    async def send(self, content: Optional[str] = None, *, embed: Optional[Any] = None) -> Any: ...

# Union type for command handlers that work with both interactions and contexts
InteractionOrContext = Union[InteractionLike, ContextLike]

# Game filtering result types
class FilterResult(TypedDict):
    matched_deals: List[Deal]
    total_matches: int
    total_games_checked: int
    priority_distribution: Dict[str, int]

class DatabaseStats(TypedDict):
    total_games: int
    priority_distribution: Dict[str, int]
    categories: List[str]

# Error types for better error handling
class APIError(TypedDict):
    error_type: str
    message: str
    status_code: Optional[int]
    retry_after: Optional[int]
