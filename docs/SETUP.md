# GameDealer Bot - Setup & Configuration

## Requirements

-   Python 3.11+
-   Discord Bot Token
-   ITAD API Key (free from [isthereanydeal.com/apps](https://isthereanydeal.com/apps/my/))

## Installation

1. **Clone Repository**

    ```bash
    git clone <repository-url>
    cd GameDealer
    ```

2. **Install Dependencies**

    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    pip install -r requirements.txt
    ```

3. **Environment Configuration**

    Create `.env` file in project root:

    ```env
    DISCORD_TOKEN=your_discord_bot_token_here
    ITAD_API_KEY=your_itad_api_key_here
    ```

4. **Run Bot**
    ```bash
    python main.py
    ```

## Configuration

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application
3. Go to "Bot" section
4. Create bot and copy token
5. Enable required intents:
    - Message Content Intent
    - Server Members Intent (if using member features)

### ITAD API Key

1. Visit [ITAD Apps Portal](https://isthereanydeal.com/apps/my/)
2. Register new app
3. Copy API key to `.env` file

### Bot Permissions

Required Discord permissions:

-   Send Messages
-   Use Slash Commands
-   Embed Links
-   Add Reactions
-   Read Message History

Invite URL:

```
https://discord.com/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=274877908032&scope=bot%20applications.commands
```

## Project Structure

```
GameDealer/
├── main.py                 # Bot entry point
├── requirements.txt        # Dependencies
├── .env                   # Environment variables (create this)
│
├── api/                   # External API integration
│   ├── http.py           # HTTP client with retry logic
│   └── itad_client.py    # ITAD API wrapper
│
├── bot/                   # Discord bot core
│   ├── core.py          # Bot initialization & command sync
│   └── scheduler.py     # Automated task scheduling
│
├── cogs/                  # Command modules
│   ├── deals.py         # Deal search commands
│   └── general.py       # Utility commands
│
├── config/                # Configuration management
│   ├── app_config.py    # Environment loading
│   └── logging_config.py # Logging setup
│
├── data/                  # Game database
│   └── priority_games.json # 1,173+ curated games
│
├── models/                # Data models
│   └── models.py        # TypedDict definitions
│
├── utils/                 # Utilities
│   ├── embeds.py        # Discord embed helpers
│   ├── game_filters.py  # Game matching logic
│   └── api_health.py    # API status checking
│
├── logs/                  # Runtime logs
└── docs/                  # Documentation
```

## Development

### Running Tests

```bash
# Run specific test
python tests/test_priority_search.py

# Debug API connectivity
python tests/debug_api.py

# Check API health
python utils/api_health.py
```

### Adding Games to Database

Edit `data/priority_games.json`:

```json
{
    "title": "Game Name",
    "priority": 8,
    "category": "RPG",
    "notes": "Optional description"
}
```

Priority scale: 1-10 (10 = GOTY winners, 1 = low quality but occasionally good deals)

### Logging

Logs are written to `logs/discord.log`. Configure level in `config/logging_config.py`.

### API Rate Limits

-   ITAD API: 100 requests/minute
-   Bot includes automatic retry logic with exponential backoff
-   Connection pooling prevents excessive connections

## Troubleshooting

### Common Issues

**"Application did not respond"**:

-   Check bot token is correct
-   Ensure bot has required permissions
-   Verify slash commands are synced

**"ITAD API errors"**:

-   Verify API key in `.env` file
-   Check API status: `python utils/api_health.py`
-   Review logs for detailed error messages

**"No games found"**:

-   Priority database only contains curated games
-   Lower `min_priority` filter to see more results
-   Check if specific game exists in `data/priority_games.json`

### Debug Commands

```bash
# Check Python environment
python --version
pip list

# Test API connectivity
python -c "import asyncio; from utils.api_health import quick_api_check; asyncio.run(quick_api_check())"

# Validate environment
python -c "from config.app_config import load_config; print('Config loaded successfully' if load_config() else 'Config error')"
```

### Performance Optimization

**For large servers** (1000+ members):

-   Enable database caching
-   Increase API connection pool size
-   Consider rate limit adjustments

**For heavy usage**:

-   Monitor `logs/discord.log` for performance metrics
-   Use `/info` command to check response times
-   Consider implementing request queuing for peak times

## Production Deployment

### Recommended Settings

```env
# Production environment
DEBUG=false
LOG_LEVEL=INFO
API_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=10
```

### Monitoring

-   Monitor `logs/discord.log` for errors
-   Use `/ping` command to check responsiveness
-   Set up API health monitoring with `utils/api_health.py`
-   Track command usage patterns

### Security

-   Keep `.env` file private (never commit to git)
-   Regularly rotate Discord bot token and API keys
-   Monitor bot permissions and server access
-   Use least-privilege principle for bot permissions

---

📋 **Need help?** Check the main [README.md](README.md) for user documentation or open an issue.
