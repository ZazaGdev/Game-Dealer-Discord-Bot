# GameDealer Bot Commands Documentation

## Overview

GameDealer is a Discord bot that helps you find the best game deals from popular stores like Steam, Epic Games Store, and GOG. The bot uses a curated database of quality games and automatically prioritizes deals by discount percentage.

**Command Types Available:**

-   **Slash Commands** (modern): `/command_name` - Type `/` and see autocomplete options
-   **Traditional Prefix Commands**: `!command_name` - Classic text-based commands

## Deal Search Commands

### 🎮 General Deal Search

**Slash Command:** `/search_deals [amount]`  
**Prefix Command:** `!search_deals [amount]`

**Description:** Search for the best deals from Steam, Epic Games Store, and GOG (prioritized stores)

**Parameters:**

-   `amount` (optional): Number of deals to show (1-25, default: 10)

**Features:**

-   Prioritizes Steam, Epic, and GOG stores
-   Shows deals sorted by highest discount percentage
-   **Only displays games from curated priority database** (1,173+ quality games)
-   Displays results in paginated format (10 deals per page)
-   Automatically filters out unknown or low-quality games

**Examples:**

```
/search_deals
/search_deals amount:15
!search_deals
!search_deals 15
```

### 🏪 Store-Specific Search

**Slash Command:** `/search_store [store] [amount]`  
**Prefix Command:** `!search_store [store] [amount]`

**Description:** Search for best deals from a specific store

**Parameters:**

-   `store` (required): Store name (e.g., Steam, Epic, GOG, etc.)
-   `amount` (optional): Number of deals to show (1-25, default: 10)

**Features:**

-   Searches specific store for quality game deals
-   Sorts results by discount percentage
-   **Only shows games from curated priority database**
-   Filters out unknown games automatically

**Examples:**

```
/search_store store:Steam
/search_store store:Epic amount:20
!search_store Steam
!search_store "Epic Games Store" 15
```

### 🎯 Priority Search (Curated Games Only)

**Slash Command:** `/priority_search [amount] [min_priority] [min_discount] [store]`  
**Prefix Command:** `!priority_search [amount] [min_priority] [min_discount] [store]`

**Description:** 🎯 **STRICT PRIORITY SEARCH** - Search ONLY for deals from your curated priority games database

**Parameters:**

-   `amount` (optional): Number of deals to show (1-25, default: 10)
-   `min_priority` (optional): Minimum priority level (1-10, default: 5)
-   `min_discount` (optional): Minimum discount percentage (1-100, default: 1)
-   `store` (optional): Store name (e.g., Steam, Epic, GOG - searches all major stores if not specified)

**Features:**

-   **100% CURATED**: Only returns games from the 1,173-game priority database
-   **Manual Matching**: Fetches all discounted games and matches against priority database
-   **Store Filtering**: Search specific store or all major stores (Steam, Epic, GOG)
-   **Priority-Based Sorting**: Games with higher priority scores rank higher
-   **Quality Guaranteed**: Every result is a vetted, quality game
-   **Advanced Filtering**: Combine priority level, discount, and store requirements
-   **Detailed Information**: Shows category, notes, and priority indicators
-   **Friendly Errors**: Clear messages when no matches are found

**Examples:**

```
/priority_search
/priority_search amount:15 min_priority:7 min_discount:50
/priority_search amount:10 store:Steam
/priority_search amount:20 min_priority:8 min_discount:30 store:Epic
!priority_search
!priority_search 15 7 50
!priority_search 10 5 1 Steam
!priority_search 20 8 30 "Epic Game Store"
```

**Use Cases:**

-   Find high-quality games with substantial discounts
-   Discover AAA titles you might have missed
-   Filter by priority level to match your gaming preferences
-   Ensure every deal is for a proven, quality game

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
