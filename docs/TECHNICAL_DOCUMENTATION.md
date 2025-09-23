# GameDealer Bot - Technical Documentation

## Project Overview

GameDealer is a Discord bot that fetches game deals from the IsThereAnyDeal (ITAD) API using modern Discord slash commands. The bot features a curated game database for quality filtering, automatic deal scheduling, and prioritized store selection focusing on Steam, Epic Games Store, and GOG.

## Architecture

### Core Design Principles

-   **Modern Slash Commands**: Full Discord slash command implementation with autocomplete
-   **Curated Quality Filtering**: Database-driven game prioritization system
-   **Scheduled Operations**: Daily deal fetching at 9 AM using Discord.py tasks
-   **Smart Store Prioritization**: Prefers Steam, Epic, GOG but includes other quality stores
-   **Pagination Support**: Handles large result sets with multiple embed pages
-   **Error Transparency**: Real error messages with helpful suggestions
-   **Clean Logging**: Centralized logging to `logs/` directory
-   **Modular Cogs**: Organized command modules for maintainability

## File Structure

```
GameDealer/
├── api/                    # External API integration
│   ├── __init__.py
│   ├── http.py            # HTTP client with retry logic
│   └── itad_client.py     # ITAD API client with priority filtering
│
├── bot/                   # Discord bot core
│   ├── __init__.py
│   ├── core.py           # Bot initialization and slash command sync
│   └── scheduler.py      # Daily deal scheduling system
│
├── cogs/                  # Discord command modules (slash commands)
│   ├── __init__.py
│   ├── deals.py          # Deal search commands with pagination
│   └── general.py        # Utility commands (ping, help, info)
│
├── config/                # Configuration management
│   ├── __init__.py
│   ├── app_config.py     # Environment variable loading
│   └── logging_config.py # Logging setup utilities
│
├── data/                  # Game database
│   └── priority_games.json # Curated game database with priority scores
│
├── docs/                  # Documentation
│   ├── COMMANDS.md       # Complete command documentation
│   ├── PRIORITY_DATABASE_GUIDE.md # Game database management
│   ├── TECHNICAL_DOCUMENTATION.md # This file
│   └── api_templates.md  # ITAD API response examples
│
├── logs/                  # Log files (auto-created)
│   ├── discord.log       # Bot operational logs
│   └── api_responses.json # API response debugging logs
│
├── models/                # Data models
│   ├── __init__.py
│   └── models.py         # Deal data structure definitions
│
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── embeds.py         # Discord embed formatting
│   └── game_filters.py   # Priority game filtering system
│
├── main.py               # Bot entry point
├── requirements.txt      # Python dependencies
└── README.md            # Project overview
```

│
├── tests/ # Test scripts
│ ├── README.md
│ ├── test_api.py # Basic API connectivity tests
│ ├── test_bot_fixes.py # Functionality validation tests
│ ├── test_new_features.py # Feature testing
│ └── test_search.py # Search functionality tests
│
├── utils/ # Utility functions
│ ├── **init**.py
│ └── embeds.py # Discord embed creation utilities
│
├── main.py # Application entry point
├── requirements.txt # Python dependencies
└── .env # Environment variables (create manually)

```

## Core Components

### 1. ITAD Client (`api/itad_client.py`)

**Primary Functionality:**

-   Fetches game deals from ITAD API v2
-   Implements store filtering using numeric shop IDs
-   Handles API errors and rate limiting
-   Logs full API responses for debugging

**Key Methods:**

-   `fetch_deals()`: Main deal fetching with store filtering
-   `_get_shop_id()`: Converts store names to ITAD shop IDs
-   `_get_title_v2()`, `_get_store_v2()`, etc.: Data extraction from API responses

**Store ID Mappings:**

-   Steam: 61
-   Epic Game Store: 16
-   GOG: 35
-   Fanatical: 6
-   Humble Store: 37
-   Green Man Gaming: 36
-   And 25+ other major stores

### 2. Bot Core (`bot/core.py`)

**Primary Functionality:**

- Discord bot initialization with slash command support
- Automatic command tree synchronization
- Cog loading with error handling
- ITAD client integration with priority filtering

**Key Features:**

- Automatic cog loading: `cogs.general`, `cogs.deals`
- Slash command sync on startup
- Clean shutdown handling
- Priority game database integration

### 3. Deal Scheduler (`bot/scheduler.py`)

**Primary Functionality:**

- Daily deal posting at 9 AM
- Administrative controls for scheduling
- Deal fetching automation

**Key Commands (Text-based, Admin only):**

- `!enable_daily_deals`: Enable automatic posting
- `!disable_daily_deals`: Disable automatic posting
- `!trigger_daily_deals`: Manual trigger

### 4. Deal Commands (`cogs/deals.py`)

**Primary Functionality:**

- Modern slash command interface
- Curated game database filtering
- Smart pagination for large result sets
- Store prioritization (Steam, Epic, GOG)

**Key Slash Commands:**

- `/search_deals [amount]`: Best deals from prioritized stores
- `/search_store [store] [amount]`: Store-specific deal search

**Advanced Features:**

- **Pagination System**: Splits large results into 10-deal pages
- **Smart Fetching**: Gets 5x requested amount to account for filtering
- **Store Prioritization**: Prefers Steam/Epic/GOG, fills with quality alternatives
- **Priority Filtering**: Uses curated database to show only quality games

**Key Commands:**

-   `!search_deals <discount> <limit> [store]`: Custom deal search
-   `!top_deals <count> [store]`: Best deals listing
-   `!list_stores`: Available store names
-   `!deals_by_store <store>`: Store-specific deals

**Advanced Features:**

-   **Multi-Embed Support**: Automatically splits large result sets (>10 deals) into multiple embeds
-   **Smart Pagination**: Creates separate messages for deals 11-20, 21-30, etc.
-   **Compact Display**: Shows original price, discount percentage, and deal links
-   **Store Filtering**: Works with all supported store names and abbreviations

**Usage Examples:**

```

!search_deals 70 15 # 15 deals with 70%+ discount
!search_deals 50 20 Steam # 20 Steam deals (multiple embeds if needed)
!search_deals 60 25 Epic Game Store # 25 Epic deals with smart pagination

````

**Multi-Embed Behavior:**

-   **1-10 deals**: Single embed
-   **11-20 deals**: Two embeds (10 + remaining)
-   **21+ deals**: Multiple embeds with page indicators

### 5. HTTP Client (`api/http.py`)

**Primary Functionality:**

-   Robust HTTP client with retry logic
-   Exponential backoff for failed requests
-   Automatic session management
-   Error handling for different HTTP status codes

**Key Features:**

-   Retries with jitter for reliability
-   Proper connection cleanup
-   Timeout handling

## Data Models

### Deal Model (`models/models.py`)

```python
class Deal(TypedDict, total=False):
    title: str                    # Game title
    price: str                   # Current price (formatted)
    store: str                   # Store name
    url: str                     # Deal URL
    discount: Optional[str]      # Discount percentage
    original_price: Optional[str] # Original price (formatted)
````

## Configuration

### Environment Variables (.env)

```env
DISCORD_TOKEN=your_discord_bot_token
LOG_CHANNEL_ID=channel_id_for_logs
DEALS_CHANNEL_ID=channel_id_for_deals
ITAD_API_KEY=your_itad_api_key
DEBUG_API_RESPONSES=false
```

### Configuration Loading (`config/app_config.py`)

-   Loads environment variables with defaults
-   Validates required configuration
-   Provides type-safe configuration access

## Logging Strategy

### Centralized Configuration (`config/logging_config.py`)

**Design Philosophy:**

-   **Single Source of Truth**: All logging configuration in one module
-   **Consistent Formatting**: Uniform log format across all components
-   **Handler Management**: Automatic cleanup and conflict prevention
-   **Separation of Concerns**: Keeps main.py clean and focused

**Key Functions:**

-   `setup_logging()`: Main configuration function with conflict prevention
-   `get_logger()`: Retrieve configured logger instances
-   `get_log_directory()`: Utility for log directory management

**Usage Pattern:**

```python
from config.logging_config import setup_logging, get_logger

# In main.py
log = setup_logging()

# In other modules
log = get_logger('module_name')
```

### Log Destinations

-   **Console**: Real-time output during development
-   **logs/discord.log**: Bot operational logs with timestamps
-   **logs/api_responses.json**: Full API responses for debugging

### Log Levels

-   **INFO**: Normal operations, startup, shutdown
-   **WARNING**: Non-critical issues, missing optional config
-   **ERROR**: Command failures, API errors, critical issues

### Configuration Features

-   **Conflict Prevention**: Automatic cleanup of existing handlers
-   **UTF-8 Encoding**: Proper Unicode support for international content
-   **Force Reconfiguration**: Ensures clean setup in all environments
-   **Centralized Management**: Single point of control for all logging

## API Integration

### ITAD API v2 Usage

**Endpoint**: `https://api.isthereanydeal.com/deals/v2`

**Key Parameters:**

-   `shops`: Comma-separated shop IDs for filtering
-   `sort`: "-cut" for highest discount first
-   `limit`: Maximum results (up to 200)
-   `nondeals`: "false" to exclude regular prices

**Error Handling:**

-   403: Invalid API key
-   429: Rate limiting
-   500+: Server errors with retry logic

## Development Workflow

### Running the Bot

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your tokens and keys

# Run the bot
python main.py
```

### Testing

```bash
# Run individual tests
python tests/test_api.py
python tests/test_bot_fixes.py

# Run all tests with pytest
pip install pytest
pytest tests/
```

### Adding New Commands

1. Add command to appropriate cog (`cogs/deals.py` or `cogs/general.py`)
2. Use proper error handling with actual error display
3. Test with Discord commands
4. Update documentation

### Adding New Stores

1. Get shop ID from ITAD API `/service/shops/v1`
2. Add mapping to `_get_shop_id()` in `itad_client.py`
3. Test store filtering functionality

## Performance Considerations

### API Rate Limiting

-   ITAD API has reasonable rate limits
-   HTTP client implements exponential backoff
-   Avoid excessive API calls in loops

### Memory Usage

-   Deal objects are lightweight TypedDict structures
-   HTTP sessions are properly closed
-   No persistent data storage (stateless design)

### Discord Rate Limiting

-   Discord.py handles rate limiting automatically
-   Avoid bulk message sending
-   Use embeds for rich formatting

## Security Best Practices

### Token Management

-   Store tokens in environment variables
-   Never commit `.env` files
-   Use different tokens for development/production

### Error Handling

-   Real errors shown in Discord for debugging
-   Sensitive information filtered from logs
-   API keys excluded from logged parameters

## Troubleshooting

### Common Issues

1. **Store filtering not working**

    - Check store name spelling
    - Verify shop ID mapping exists
    - Use `!list_stores` for available stores

2. **No deals found**

    - Lower discount threshold
    - Remove store filter
    - Check API key validity

3. **Bot not responding**
    - Verify Discord token
    - Check bot permissions in server
    - Review logs/discord.log for errors

### Debug Mode

Enable debug API responses:

```env
DEBUG_API_RESPONSES=true
```

This logs full API responses to `logs/api_responses.json` for analysis.

## Future Enhancements

### Potential Improvements

-   Game price tracking and alerts
-   User-specific deal preferences
-   Deal comparison across stores
-   Historical price data integration
-   Advanced filtering (genres, ratings, etc.)

### Architecture Considerations

-   Database integration for user preferences
-   Caching layer for frequently accessed data
-   Webhook support for real-time deal notifications
-   Multiple API source integration

## Contributing

### Code Style

-   Follow PEP 8 conventions
-   Use type hints where appropriate
-   Add docstrings for public methods
-   Keep functions focused and small

### Testing

-   Add tests for new functionality
-   Verify error handling paths
-   Test Discord command interaction
-   Validate API integration changes
