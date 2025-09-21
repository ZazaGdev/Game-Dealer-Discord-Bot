# GameDealer Bot - Simplified Version

A Discord bot that fetches game deals from IsThereAnyDeal (ITAD) API and posts them on a schedule.

## Simplified Architecture (No Webhooks)

This version removes the webhook server since you mentioned you're only doing scheduled requests and not hosting the bot for external notifications.

## Files Structure

### Core Files

-   `main_simple.py` - Main entry point without webhook server
-   `bot/scheduler.py` - Handles scheduled deal fetching (daily at 9 AM)
-   `requirements_simple.txt` - Minimal dependencies (no FastAPI/uvicorn)

### Keep These Folders

-   `api/` - ITAD API client (fully functional)
-   `bot/` - Discord bot core and scheduler
-   `cogs/` - Bot commands (deals, general)
-   `config/` - Configuration management
-   `models/` - Data models
-   `utils/` - Utility functions (embeds)

### Can Remove These Folders

-   `webhook/` - Not needed for scheduled requests
-   `docs/` - Optional (has API templates if you need reference)
-   `logs/` - Will be recreated automatically

## Setup

1. **Install simplified dependencies:**

    ```bash
    pip install -r requirements_simple.txt
    ```

2. **Configure environment variables (.env):**

    ```
    DISCORD_TOKEN=your_discord_bot_token
    ITAD_API_KEY=your_itad_api_key
    DEALS_CHANNEL_ID=your_discord_channel_id
    LOG_CHANNEL_ID=your_log_channel_id  # Optional
    DEBUG_API_RESPONSES=true  # Optional, for API response logging
    ```

3. **Run the bot:**
    ```bash
    python main_simple.py
    ```

## Features

### Scheduled Daily Deals

-   Automatically fetches and posts deals daily at 9 AM
-   Configurable minimum discount (default: 60%)
-   Posts the best deal to your configured Discord channel

### Manual Commands

-   `!deals [game_name]` - Search for specific game deals
-   `!test_deals` - Test the deal posting system
-   `!enable_daily_deals` - Enable automatic daily posting (admin only)
-   `!disable_daily_deals` - Disable automatic daily posting (admin only)
-   `!trigger_daily_deals` - Manually trigger daily deal fetch (admin only)

### API Response Logging

-   When `DEBUG_API_RESPONSES=true`, saves full API responses to `logs/api_responses.json`
-   Useful for debugging and understanding the data structure

## Architecture Benefits

✅ **Simplified**: No webhook server, no FastAPI dependencies
✅ **Scheduled**: Timer-based deal fetching instead of event-driven
✅ **Modular**: Clean separation of concerns (API, bot, scheduler)
✅ **Configurable**: Easy environment-based configuration
✅ **Logged**: Comprehensive logging for debugging

## How It Works

1. Bot starts and loads the scheduler cog
2. Scheduler sets up a daily task at 9 AM
3. When triggered, it fetches deals with 60%+ discount
4. Posts the best deal to your Discord channel
5. Manual commands still work for on-demand searching

This is perfect for your use case since you're not hosting externally and just want scheduled deal notifications!
