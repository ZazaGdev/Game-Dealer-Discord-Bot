# GameDealer Bot - Technical Reference

## Architecture Overview

GameDealer is a Discord bot built with Discord.py that integrates with the IsThereAnyDeal (ITAD) API to provide curated game deal searches. The bot emphasizes quality over quantity through a manually curated game database and intelligent filtering.

### Key Technical Features

-   **Modern Discord Integration**: Full slash command support with autocomplete
-   **Exact Title Matching**: Prevents false positives using normalized string comparison
-   **Curated Quality Database**: 1,173+ games with priority ratings (1-10 scale)
-   **Robust Error Handling**: Graceful API failure management with user-friendly messages
-   **Automated Scheduling**: Daily deal updates at 9 AM using Discord.py tasks
-   **Connection Pooling**: Efficient HTTP client with retry logic and timeouts

### Component Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Discord Bot   │◄──►│   ITAD API       │◄──►│ Priority Games  │
│   (Cogs System) │    │   (HTTP Client)  │    │ Database (JSON) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Slash Commands  │    │ Retry Logic &    │    │ Exact Matching  │
│ & Embeds        │    │ Rate Limiting    │    │ & Filtering     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Core Components

### 1. API Layer (`api/`)

**`http.py`**: HTTP client wrapper with:

-   Exponential backoff retry logic
-   Connection pooling and timeout handling
-   JSON response validation
-   Enhanced error messages for 5xx server errors

**`itad_client.py`**: ITAD API integration with:

-   Deal fetching from multiple stores
-   Priority game filtering and matching
-   Store-specific search capabilities
-   Comprehensive error handling and logging

### 2. Bot Core (`bot/`)

**`core.py`**: Discord bot initialization:

-   Automatic slash command synchronization
-   Cog loading and error handling
-   Graceful shutdown procedures

**`scheduler.py`**: Automated task management:

-   Daily deal refresh at 9:00 AM
-   Background task error recovery
-   Configurable scheduling intervals

### 3. Commands (`cogs/`)

**`deals.py`**: Primary deal search functionality:

-   `/search_deals`: General deal browsing
-   `/search_store`: Store-specific searches
-   `/priority_search`: Curated quality games with exact matching
-   Paginated embed responses with reaction controls

**`general.py`**: Utility commands:

-   `/ping`: Latency testing
-   `/info`: Bot statistics and status
-   `/help`: Command reference
    │ └── api_templates.md # ITAD API response examples
    │
    ├── logs/ # Log files (auto-created)
    │ ├── discord.log # Bot operational logs
    │ └── api_responses.json # API response debugging logs
    │
    ├── models/ # Data models
    │ ├── **init**.py
    │ └── models.py # Deal data structure definitions
    │
    ├── utils/ # Utility modules
    │ ├── **init**.py
    │ ├── embeds.py # Discord embed formatting
    │ └── game_filters.py # Priority game filtering system
    │
    ├── main.py # Bot entry point
    ├── requirements.txt # Python dependencies
    └── README.md # Project overview

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

-   Discord bot initialization with slash command support
-   Automatic command tree synchronization
-   Cog loading with error handling
-   ITAD client integration with priority filtering

**Key Features:**

-   Automatic cog loading: `cogs.general`, `cogs.deals`
-   Slash command sync on startup
-   Clean shutdown handling
-   Priority game database integration

### 3. Deal Scheduler (`bot/scheduler.py`)

**Primary Functionality:**

-   Daily deal posting at 9 AM
-   Administrative controls for scheduling
-   Deal fetching automation

**Key Commands (Text-based, Admin only):**

-   `!enable_daily_deals`: Enable automatic posting
-   `!disable_daily_deals`: Disable automatic posting
-   `!trigger_daily_deals`: Manual trigger

### 4. Deal Commands (`cogs/deals.py`)

**Primary Functionality:**

-   Modern slash command interface
-   Curated game database filtering
-   Smart pagination for large result sets
-   Store prioritization (Steam, Epic, GOG)

**Key Slash Commands:**

-   `/search_deals [amount]`: Best deals from prioritized stores
-   `/search_store [store] [amount]`: Store-specific deal search
-   `/priority_search [amount] [min_priority] [min_discount]`: **NEW** - Strict priority-only search

**Advanced Features:**

-   **Strict Priority Filtering**: Only returns games that match the curated priority database
-   **Priority-Based Sorting**: When discount >50%, priority takes precedence over discount amount
-   **Pagination System**: Splits large results into 10-deal pages
-   **Smart Fetching**: Gets 10-15x requested amount to account for strict priority filtering
-   **Store Prioritization**: Prefers Steam/Epic/GOG, filters to priority games only
-   **Quality Assurance**: Uses curated database to guarantee all results are quality games

### Priority-Based Sorting Logic

**NEW FEATURE**: Smart sorting that balances priority scores with discount percentages:

-   **High Discount Deals (>50%)**: Sorted by priority first, then discount
    -   Example: Priority 9 game with 60% discount ranks higher than Priority 7 game with 80% discount
-   **Low Discount Deals (≤50%)**: Sorted by discount first, then priority
    -   Traditional discount-focused sorting for moderate deals
-   **Ensures Quality**: Higher priority games are favored when both deals offer substantial savings

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

```

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
```

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

### Code Style & Type Safety

-   **Comprehensive Type Annotations**: All functions use proper type hints
-   **TypedDict Definitions**: Structured data uses TypedDict for validation
-   **Protocol Interfaces**: Duck typing with Protocol classes
-   **Union Types**: Flexible parameter handling with Union types
-   **Optional Types**: Explicit nullable value handling
-   Follow PEP 8 conventions
-   Add docstrings for public methods
-   Keep functions focused and small

### Type System Components

**Models (`models/models.py`)**:

-   `PriorityGame`: Game database structure
-   `ITADGameItem`, `ITADShop`, `ITADPrice`: API response types
-   `InteractionLike`: Protocol for Discord interactions
-   `FilterResult`: Search filtering results
-   `DatabaseStats`: Priority database statistics

**Benefits**:

-   Early error detection during development
-   Better IDE support and autocomplete
-   Self-documenting code structure
-   Reduced runtime errors

### Testing

-   Add tests for new functionality
-   Verify error handling paths
-   Test Discord command interaction
-   Validate API integration changes
