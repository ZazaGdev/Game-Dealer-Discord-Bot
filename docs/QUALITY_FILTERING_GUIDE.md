# Quality Game Filtering System

## Overview

GameDealer now includes an intelligent quality filtering system that automatically filters out educational content, courses, and tutorials to focus on actual video games. This ensures users get relevant game deals instead of mixed results.

## Features

### 🎯 Content-Based Filtering

-   **Keyword Detection**: Identifies and filters out courses, tutorials, programming content
-   **Pattern Matching**: Uses regex to catch educational content patterns
-   **Store Quality Assessment**: Prioritizes deals from reputable gaming platforms
-   **No Price Filtering**: Preserves great deals on AAA games regardless of price

### 🎮 Smart Recognition

-   Keeps actual video games, DLCs, and game-related content
-   Filters out programming courses, software training, and educational materials
-   Recognizes quality gaming stores vs educational platforms

## Commands

### Quality Filtering Enabled (Default)

-   `!search_deals` - Search for quality game deals
-   `!quality_deals` - Explicitly search for quality games only
-   `!top_deals` - Get top quality game deals
-   `!deals_by_store` - Quality games from specific store

### All Content (No Filtering)

-   `!search_all_deals` - Include courses and tutorials
-   Use when you specifically need to see everything

### Information Commands

-   `!filtering_help` - Show detailed filtering guide
-   `!test_api` - Test API and show filtering statistics

## Technical Implementation

### Files Created/Modified

-   `utils/game_filters.py` - Core filtering logic
-   `api/itad_client.py` - Integrated quality filtering
-   `cogs/deals.py` - Updated Discord commands
-   `utils/__init__.py` - Export filtering functions

### Quality Filter Class

```python
class GameQualityFilter:
    def is_quality_game(title, store) -> bool
    def is_quality_store(store) -> bool
    def has_non_game_keywords(title) -> bool
    def matches_non_game_patterns(title) -> bool
    def validate_game_title(title) -> bool
```

## Filter Criteria

### What Gets Filtered Out ❌

-   Programming courses and tutorials
-   Software training and certifications
-   Educational/learning platforms content
-   Non-game digital products
-   Content from low-quality stores

### What Stays In ✅

-   Actual video games of all genres
-   Game DLCs and expansions
-   Game soundtracks and digital extras
-   Content from reputable gaming stores
-   All price ranges (no price discrimination)

## Usage Examples

```discord
# Quality games only (default)
!search_deals 60 10
!top_deals 5 Steam

# All content including courses
!search_all_deals 60 10

# Store-specific quality games
!deals_by_store Epic Game Store

# Get help and statistics
!filtering_help
!test_api
```

## Benefits

1. **Better User Experience**: Users see relevant game deals immediately
2. **Time Saving**: No need to manually filter through courses and tutorials
3. **Quality Assurance**: Focus on actual games from reputable stores
4. **Flexibility**: Can still access all content when needed
5. **Price Preservation**: Great deals on expensive games are not filtered out

## Testing Results

The filtering system successfully:

-   Identifies real games (Cyberpunk 2077, Elden Ring, etc.)
-   Filters out educational content (Python courses, programming tutorials)
-   Maintains approximately 50% filter effectiveness on mixed content
-   Preserves all price ranges to catch amazing deals

## Configuration

The system is enabled by default but can be controlled via the `quality_filter` parameter in the ITAD client:

```python
# Quality filtering enabled (default)
deals = await client.fetch_deals(quality_filter=True)

# No filtering
deals = await client.fetch_deals(quality_filter=False)
```
