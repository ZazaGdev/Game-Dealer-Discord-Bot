# Game Database Management

## Overview

The `data/priority_games.json` file contains 1,173+ curated games with priority ratings. This database powers the quality filtering system that ensures users only see worthwhile deals instead of random low-quality games.

## Adding New Games

### Basic Entry Format

```json
{
    "title": "Game Name",
    "priority": 8,
    "category": "RPG",
    "notes": "Brief description or franchise info"
}
```

### Priority Rating Scale

| Rating  | Quality Level   | Examples                               |
| ------- | --------------- | -------------------------------------- |
| **10**  | GOTY Winners    | The Witcher 3, Elden Ring, Hades       |
| **9**   | Exceptional AAA | Cyberpunk 2077, Red Dead Redemption 2  |
| **8**   | Great Games     | Hollow Knight, Divinity Original Sin 2 |
| **7**   | Solid Titles    | Assassin's Creed series, Rocket League |
| **6**   | Good Niche      | Stardew Valley, Among Us               |
| **5**   | Casual/OK       | Various simulator games                |
| **1-4** | Lower Quality   | Still included for amazing deals       |

### Title Matching (Important!)

The bot uses **exact matching** with special character normalization:

✅ **Good Entry**: `"title": "Raft"`

-   Matches: "Raft", "Raft™", "Raft®"
-   Does NOT match: "Minecraft: Raft Edition", "Raft Survival Multiplayer"

✅ **Franchise Entry**: `"title": "Call of Duty"`

-   Matches: "Call of Duty: Modern Warfare", "Call of Duty Black Ops"

❌ **Avoid Generic Terms**: `"title": "Survival"`

-   Would match too many unrelated games

### Categories

Use consistent category names:

-   **RPG**, **Action**, **Adventure**, **Strategy**, **Simulation**
-   **Shooter**, **Racing**, **Sports**, **Puzzle**, **Indie**
-   **MMO**, **Roguelike**, **Platformer**, **Fighting**

```json
{"title": "Grand Theft Auto", "priority": 9, "category": "Action"},
{"title": "GTA", "priority": 9, "category": "Action"}
```

#### Use Franchise Names for Series

```json
{ "title": "Call of Duty", "priority": 8, "category": "FPS" }
```

Matches all COD games: Modern Warfare, Black Ops, etc.

### 4. Category Guidelines

Use descriptive categories that help organize games:

-   **RPG**: Role-playing games
-   **FPS**: First-person shooters
-   **Action/Adventure**: Action-adventure games
-   **Strategy**: Strategy games (RTS, TBS)
-   **Simulation**: Simulation games
-   **Indie**: Independent games
-   **Horror**: Horror games
-   **Racing**: Racing games
-   **Sports**: Sports games
-   **Puzzle**: Puzzle games

### 5. Example Entries

```json
{
  "title": "Baldur's Gate 3",
  "priority": 10,
  "category": "RPG",
  "notes": "2023 GOTY winner, incredible D&D RPG"
},
{
  "title": "Hades",
  "priority": 9,
  "category": "Roguelike",
  "notes": "Supergiant's masterpiece roguelike"
},
{
  "title": "Dead Cells",
  "priority": 7,
  "category": "Metroidvania",
  "notes": "Excellent indie metroidvania"
}
```

## Quick Tips for Population

### Research Sources

1. **Metacritic**: Check highest-rated games
2. **Steam**: Top sellers and highest-rated
3. **Game Awards**: GOTY winners and nominees
4. **Reddit**: r/GameDeals, r/patientgamers discussions
5. **IGN/GameSpot**: Top games lists

### Batch Adding Strategy

1. Start with obvious 10/10 games (GOTY winners)
2. Add popular AAA franchises (COD, Assassin's Creed, etc.)
3. Include acclaimed indie games
4. Add niche but quality games in specific genres
5. Include games you personally recommend

### Efficiency Tips

-   Add franchise names to catch entire series
-   Include both full and shortened titles
-   Focus on games that frequently go on sale
-   Prioritize games your Discord community would enjoy

## Current Database Stats

The database currently contains 80+ games across all categories:

-   Priority 10: 3 games (GOTY-level)
-   Priority 9: 12 games (Exceptional)
-   Priority 8: 19 games (Great)
-   Priority 7: 28 games (Good)
-   Priority 6: 13 games (Decent)
-   Priority 5: 5 games (OK)

## How the System Works

1. **Smart Matching**: The system finds games using partial title matching
2. **Priority Sorting**: Results are sorted by priority score first, then match quality
3. **Flexible Filtering**: Commands can request different minimum priority levels
4. **No False Positives**: Only curated games appear in results

## Commands That Use This Database

-   `!search_deals` - Default priority 5+ filtering
-   `!priority_deals <level>` - Custom priority filtering
-   `!quality_deals` - Priority 5+ games
-   `!top_deals` - Quick priority 5+ search
-   `!test_api` - Shows filtering statistics

## Maintenance

-   **Regular Updates**: Add new releases and popular games
-   **Community Input**: Ask Discord users for game recommendations
-   **Sales Analysis**: Check what games frequently have good deals
-   **Seasonal Updates**: Add holiday/seasonal favorites

The more games you add to this database, the better the filtering becomes!
