# Priority Games Database Guide

## Overview

The `priority_games.json` file contains a curated database of quality games with priority scores. This system is used by the `/search_deals` and `/search_store` slash commands to filter and prioritize game deals, ensuring users see only quality games rather than unknown or low-quality titles.

## How to Add Games

### 1. Basic Game Entry Structure

```json
{
    "title": "Game Name",
    "priority": 8,
    "category": "Genre",
    "notes": "Optional description or notes"
}
```

### 2. Priority Scoring Scale (1-10)

-   **10**: Game of the Year winners, absolute must-haves (e.g., The Witcher 3, Elden Ring)
-   **9**: Exceptional AAA games, universally acclaimed (e.g., Cyberpunk 2077, Red Dead Redemption 2)
-   **8**: Great games, very popular and well-reviewed (e.g., Call of Duty, Hollow Knight)
-   **7**: Good games, solid titles worth playing (e.g., Assassin's Creed, Rocket League)
-   **6**: Decent games, niche appeal or specific audiences (e.g., Among Us, Stardew Valley)
-   **5**: OK games, casual or specific interest (e.g., Truck Simulator)
-   **4**: Below average but playable
-   **3**: Mediocre games
-   **2**: Poor quality games
-   **1**: Very low quality but might occasionally have amazing deals

### 3. Title Matching Strategy

The system uses intelligent partial matching, so you can:

#### Use Core Game Names

```json
{ "title": "Witcher 3", "priority": 10, "category": "RPG" }
```

This will match:

-   "The Witcher 3: Wild Hunt"
-   "Witcher 3: Complete Edition"
-   "The Witcher 3 - Game of the Year Edition"

#### Include Multiple Variations

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
