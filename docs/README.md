# GameDealer Bot Documentation

🎮 **GameDealer** is a Discord bot that finds the best game deals from Steam, Epic Games Store, GOG, and other popular stores using a curated database of quality games.

## Quick Start

### Commands Overview

| Command            | Purpose                    | Example                                           |
| ------------------ | -------------------------- | ------------------------------------------------- |
| `/search_deals`    | Best deals from all stores | `/search_deals amount:15`                         |
| `/search_store`    | Deals from specific store  | `/search_store store:Steam amount:10`             |
| `/priority_search` | Curated quality games only | `/priority_search min_priority:8 min_discount:50` |
| `/ping`            | Check bot latency          | `/ping`                                           |
| `/info`            | Bot statistics             | `/info`                                           |
| `/help`            | Show commands              | `/help`                                           |

### Command Types

-   **Slash Commands** (recommended): `/command` - Modern Discord commands with autocomplete
-   **Prefix Commands**: `!command` - Traditional text-based commands

## Key Features

✅ **Curated Game Database**: 1,173+ quality games with priority ratings  
✅ **Exact Title Matching**: Prevents false positives ("Raft" won't match "Minecraft: Raft Edition")  
✅ **Smart Store Prioritization**: Focuses on Steam, Epic, GOG first  
✅ **Advanced Filtering**: By priority level, discount percentage, and store  
✅ **Automated Daily Updates**: Fresh deals every morning at 9 AM

## Command Details

### 🎯 Priority Search (Recommended)

**Best for**: Finding quality games on sale

```bash
# Basic search - quality games with any discount
/priority_search

# High-quality games with big discounts
/priority_search min_priority:8 min_discount:50

# Search specific store
/priority_search store:Steam min_priority:7 min_discount:30
```

**Parameters**:

-   `amount` (1-25, default: 10): Number of deals to show
-   `min_priority` (1-10, default: 5): Minimum game quality level
    -   🏆 **9-10**: Premium (GOTY winners, must-haves)
    -   ⭐ **7-8**: High quality (popular, well-reviewed)
    -   ✨ **5-6**: Good games (solid titles, worth playing)
    -   📦 **1-4**: Standard (niche or casual games)
-   `min_discount` (1-100%, default: 1): Minimum discount percentage
-   `store` (optional): Specific store name (Steam, Epic, GOG, etc.)

### 🛒 General Deal Search

**Best for**: Browsing all available deals

```bash
# Top deals from preferred stores (Steam, Epic, GOG)
/search_deals amount:20

# Deals from specific store
/search_store store:"Epic Games Store" amount:15
```

## Priority Rating System

Our curated database rates games 1-10 based on quality, popularity, and reviews:

| Rating  | Category         | Examples                               |
| ------- | ---------------- | -------------------------------------- |
| **10**  | Game of the Year | The Witcher 3, Elden Ring, Hades       |
| **9**   | Exceptional AAA  | Cyberpunk 2077, Red Dead Redemption 2  |
| **8**   | Great Games      | Hollow Knight, Divinity Original Sin 2 |
| **7**   | Solid Titles     | Assassin's Creed series, Rocket League |
| **6**   | Good Niche       | Stardew Valley, Among Us               |
| **5-1** | Casual/Specific  | Various indie and specialized games    |

## Supported Stores

**Primary Stores** (prioritized):

-   Steam
-   Epic Games Store
-   GOG (Good Old Games)

**Additional Stores**:

-   Humble Bundle, Green Man Gaming, Fanatical, GamesPlanet, and 20+ others

## Tips & Best Practices

💡 **For Best Results**:

-   Use `/priority_search` for quality game discovery
-   Set `min_priority:7` or higher for well-reviewed games
-   Use `min_discount:50` to find significant sales
-   Try different store parameters to compare prices

💡 **Finding Specific Games**:

-   The bot only shows games from our curated database
-   If a game isn't appearing, it might not be in our priority list
-   Use `/search_store` to see all deals from a specific store

💡 **Daily Deal Updates**:

-   Bot automatically fetches fresh deals every morning at 9 AM
-   No need to manually refresh - deals stay current

## Troubleshooting

**"No deals found"**: Try lowering `min_priority` or `min_discount` filters  
**Missing games**: Game might not be in our curated database  
**API errors**: Service might be temporarily unavailable, try again later  
**Slow responses**: Bot might be fetching fresh data, please wait

---

📋 **Need Help?** Use `/help` in Discord or contact the bot administrator.

🔧 **Technical Details**: See [SETUP.md](SETUP.md) for installation and configuration.
