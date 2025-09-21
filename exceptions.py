# exceptions.py - Custom exception hierarchy for GameDealer bot
"""
Custom exceptions for better error handling and debugging.
"""

class GameDealerError(Exception):
    """Base exception for all GameDealer bot errors."""
    pass

class ConfigurationError(GameDealerError):
    """Raised when configuration is invalid or missing."""
    pass

class APIError(GameDealerError):
    """Base class for API-related errors."""
    pass

class ITADAPIError(APIError):
    """Raised when ITAD API requests fail."""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class RateLimitError(ITADAPIError):
    """Raised when API rate limit is exceeded."""
    pass

class AuthenticationError(ITADAPIError):
    """Raised when API authentication fails."""
    pass

class StoreNotFoundError(GameDealerError):
    """Raised when a requested store is not found in the shop mappings."""
    def __init__(self, store_name: str):
        super().__init__(f"Store '{store_name}' not found in supported stores")
        self.store_name = store_name

class DiscordError(GameDealerError):
    """Base class for Discord-related errors."""
    pass

class ChannelNotFoundError(DiscordError):
    """Raised when a Discord channel cannot be found."""
    def __init__(self, channel_id: int):
        super().__init__(f"Channel with ID {channel_id} not found")
        self.channel_id = channel_id

class PermissionError(DiscordError):
    """Raised when bot lacks required Discord permissions."""
    pass