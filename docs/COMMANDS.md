# GameDealer Bot Commands Documentation

## Overview

GameDealer is a Discord bot that helps you find the best game deals from popular stores like Steam, Epic Games Store, and GOG. The bot uses a curated database of quality games and automatically prioritizes deals by discount percentage.

## User Commands (Slash Commands)

### 🎮 Deal Search Commands

#### `/search_deals [amount]`

**Description:** Search for the best deals from Steam, Epic Games Store, and GOG (prioritized stores)

**Parameters:**

-   `amount` (optional): Number of deals to show (1-25, default: 10)

**Features:**

-   Prioritizes Steam, Epic, and GOG stores
-   Shows deals sorted by highest discount percentage
-   Uses curated game database for quality filtering
-   Displays results in paginated format (10 deals per page)

**Examples:**

```
/search_deals
/search_deals amount:15
/search_deals amount:25
```

#### `/search_store [store] [amount]`

**Description:** Search for best deals from a specific store

**Parameters:**

-   `store` (required): Store name (e.g., Steam, Epic, GOG, etc.)
-   `amount` (optional): Number of deals to show (1-25, default: 10)

**Features:**

-   Searches specific store for quality game deals
-   Sorts results by discount percentage
-   Uses quality filtering from curated database

**Examples:**

```
/search_store store:Steam
/search_store store:Epic amount:20
/search_store store:GOG amount:15
/search_store store:"Epic Games Store" amount:10
```

### 🛠️ Utility Commands

#### `/ping`

**Description:** Test bot responsiveness and check latency

**Examples:**

```
/ping
```

#### `/help`

**Description:** Show all available commands with examples

**Examples:**

```
/help
```

#### `/info`

**Description:** Display bot information and statistics

**Features:**

-   Shows bot latency
-   Displays number of servers and users
-   Shows game database statistics
-   Lists supported stores

**Examples:**

```
/info
```

## Administrator Commands (Text Commands)

### 📅 Scheduler Management

_Note: These commands require administrator permissions and use the old text-based format_

#### `!enable_daily_deals`

**Description:** Enable automatic daily deal posting
**Permissions:** Administrator only

#### `!disable_daily_deals`

**Description:** Disable automatic daily deal posting
**Permissions:** Administrator only

#### `!trigger_daily_deals`

**Description:** Manually trigger daily deal posting
**Permissions:** Administrator only

## Features & Technical Details

### 🎯 Smart Deal Filtering

-   **Curated Database:** Uses a hand-picked database of 80+ quality games
-   **Priority Scoring:** Games ranked 1-10 based on quality and popularity
-   **Store Prioritization:** Prefers Steam, Epic, and GOG but includes other quality stores
-   **Discount Sorting:** Always shows highest discount percentages first

### 📊 Result Display

-   **Pagination:** Large results split into multiple pages (10 deals per page)
-   **Rich Embeds:** Formatted displays with game titles, prices, stores, and discounts
-   **Direct Links:** Click-to-visit links for each deal
-   **Priority Indicators:** Emoji indicators for game quality levels

### 🔄 Automatic Features

-   **Daily Scheduling:** Automatically posts daily deals at 9 AM
-   **Quality Filtering:** Filters out low-quality games and content
-   **Smart Fetching:** Gets more deals than requested to account for filtering
-   **Error Handling:** Graceful handling of API issues and edge cases

## Usage Tips

### Getting the Best Results

1. **Use `/search_deals`** for general browsing - it prioritizes the best stores
2. **Use `/search_store`** when you want deals from a specific platform
3. **Request more deals** (up to 25) for better selection - results are paginated
4. **Check priority indicators** - 🏆⭐✨ indicate higher quality games

### Store Names

Common store names you can use with `/search_store`:

-   `Steam`
-   `Epic` or `Epic Games Store`
-   `GOG`
-   `PlayStation Store`
-   `Xbox Store`
-   `Nintendo eShop`
-   `Humble Store`
-   `GameStop`
-   `Amazon`

### Deal Information

Each deal shows:

-   **Game Title** - Truncated if too long
-   **Current Price** - Bold formatting
-   **Original Price** - Strikethrough if available
-   **Store Name** - Where to buy the game
-   **Discount Percentage** - How much you save
-   **Priority Indicator** - Quality rating emoji
-   **Direct Link** - Click to visit the deal

## Examples in Action

### Basic Deal Search

```
/search_deals amount:10
```

Result: Shows 10 best deals from Steam, Epic, and GOG

### Store-Specific Search

```
/search_store store:Steam amount:20
```

Result: Shows 20 best Steam deals in 2 pages (10 deals each)

### Large Search with Pagination

```
/search_deals amount:25
```

Result: Shows 25 deals across 3 pages:

-   Page 1: Deals 1-10
-   Page 2: Deals 11-20
-   Page 3: Deals 21-25

## Troubleshooting

### No Deals Found

If you get "No deals found":

1. Try a different store name
2. Check if the store is currently having sales
3. Lower your expectations - some stores may not have quality games on sale

### Bot Not Responding

1. Check bot permissions in your server
2. Ensure bot has "Use Slash Commands" permission
3. Try `/ping` to test connectivity

### Commands Not Showing

1. Make sure you're typing `/` to see slash commands
2. Bot might need to sync commands (restart bot)
3. Check you have permission to use commands in the channel

## Support

For issues or questions:

1. Use `/help` to see current commands
2. Use `/info` to check bot status
3. Check bot permissions if commands aren't working
