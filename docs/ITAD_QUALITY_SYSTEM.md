# ITAD Quality Filtering System

## Overview

We've implemented a comprehensive quality filtering system that replicates ITAD's approach to showing "interesting games" instead of low-quality asset flips. This system addresses your request: _"look at this page, you'll notice that all listings are actually interesting games, how can we achieve the same?"_

## 🔍 **How ITAD Shows Quality Games**

Based on analysis of ITAD's website and API documentation, they achieve quality by:

1. **Community-Driven Popularity**: Using waitlisted and collected game counts
2. **"Hottest Games" Sorting**: Prioritizing games that people actually want
3. **Quality Metrics**: Leveraging user behavior data to identify good games
4. **Asset Flip Prevention**: Filtering out obvious low-quality games

## 🚀 **Our Implementation**

### **1. ITAD Quality Filter (`utils/itad_quality.py`)**

#### **Game Popularity Statistics**

-   Fetches data from ITAD's stats endpoints:
    -   `/stats/most-waitlisted/v1` - Games people want to buy
    -   `/stats/most-collected/v1` - Games people actually own
    -   `/stats/most-popular/v1` - Combined popularity metrics

#### **Quality Scoring Algorithm**

```python
# Quality score calculation (0-100):
base_score = min(80, popularity_score / 10)
waitlist_bonus = min(10, waitlisted_count / 100)  # Future demand
collection_bonus = min(10, collected_count / 500)  # Proven quality
final_score = base_score + waitlist_bonus + collection_bonus
```

#### **Quality Thresholds**

-   **Minimum Popular**: 10+ waitlisted OR 50+ collected OR 30+ combined
-   **High Quality**: 60+ quality score
-   **Title Matching**: Fuzzy matching handles editions and variations

### **2. Enhanced Asset Flip Detection**

#### **Multi-Criteria Detection**

-   **Price Analysis**: Very cheap games ($0.50-$1.00) with high discounts (80%+)
-   **Title Patterns**: Generic names like "Simulator 2", "Zombie X", "Battle Royale"
-   **Keyword Analysis**: 65+ meaningless words filter with ratio detection
-   **Community Validation**: Cross-reference with popularity data

#### **Red Flag Patterns**

-   Generic titles: "Word Simulator", "X Tycoon", "Zombie Adventure"
-   Suspicious pricing: $0.49 with 95% discount
-   Low complexity: Single word titles, number suffixes
-   Asset flip keywords: Over 60% generic terms

### **3. New ITAD Client Method**

#### **`fetch_quality_deals_itad_method()`**

```python
deals = await client.fetch_quality_deals_itad_method(
    limit=10,
    min_discount=50,
    sort_by="hottest",  # Use ITAD's popularity sorting
    store_filter="steam",
    use_popularity_stats=True
)
```

#### **Features**

-   **ITAD Sorting Options**:
    -   `"hottest"` - Most popular/waitlisted games (like ITAD website)
    -   `"newest"` - Recently added deals
    -   `"price"` - Lowest price first
    -   `"discount"` - Highest discount first
-   **Smart Filtering**: Requests 10x more deals, then filters for quality
-   **Quality Ranking**: Sorts by popularity score, then discount
-   **Asset Flip Prevention**: Removes obvious low-quality games

## 🎮 **New Discord Command**

### **`!quality_deals` Command**

```bash
# Basic usage
!quality_deals

# With parameters
!quality_deals steam 60 hottest

# Aliases
!quality
!q
!interesting
```

#### **Parameters**

-   **store**: `steam`, `epic`, `gog` (optional)
-   **min_discount**: Minimum discount % (default: 50)
-   **sort_by**: `hottest`, `newest`, `price`, `discount` (default: hottest)

#### **Example Output**

```
🌟 Quality Game Deals (Hottest Sort)
Showing 10 interesting games (50%+ discount)

⭐ The Witcher 3: Wild Hunt - $9.99 (75% off) on Steam
🎯 https://store.steampowered.com/app/292030

✨ Cyberpunk 2077 - $29.99 (50% off) on Steam
🎯 https://store.steampowered.com/app/1091500

✨ Curated using ITAD's popularity data and quality filtering
```

## 📊 **Quality vs Priority Search Comparison**

| Feature                   | Priority Search      | Quality Deals             |
| ------------------------- | -------------------- | ------------------------- |
| **Data Source**           | Local JSON database  | ITAD popularity stats     |
| **Games Covered**         | 1,173 curated games  | All popular games on ITAD |
| **Update Frequency**      | Manual updates       | Real-time via API         |
| **Quality Method**        | Human curation       | Community-driven metrics  |
| **Asset Flip Prevention** | Manual exclusion     | Automated detection       |
| **Sorting**               | Priority score first | Popularity + discount     |

## 🔧 **Technical Implementation**

### **Quality Score Calculation**

1. **Fetch Popularity Data**: Load community stats from ITAD
2. **Calculate Quality Score**: Combine waitlist + collection metrics
3. **Asset Flip Detection**: Multi-pattern analysis
4. **Smart Sorting**: Popularity-first, discount-secondary
5. **Title Matching**: Fuzzy matching for variations

### **Caching Strategy**

-   **Popularity Data**: 1-hour cache to avoid API limits
-   **Quality Scores**: Calculated dynamically per request
-   **Asset Flip Detection**: Real-time analysis

### **Error Handling**

-   **API Failures**: Graceful fallback to basic filtering
-   **Missing Data**: Default quality scores for unknown games
-   **Rate Limits**: Intelligent request batching

## 🎯 **Results Expected**

### **Before (Regular Deals)**

-   Mixed quality games including asset flips
-   Price-focused sorting
-   No community validation
-   Many low-quality $0.50 games

### **After (Quality Deals)**

-   Only community-validated games
-   Popularity-driven selection
-   Automatic asset flip removal
-   Games people actually want

## 🚀 **Usage Examples**

### **Find Popular Steam Games**

```bash
!quality_deals steam 30 hottest
```

_Shows trending/popular Steam games with 30%+ discounts_

### **Best Value Games**

```bash
!quality_deals 70 price
```

_Shows quality games with high discounts, sorted by price_

### **New Quality Deals**

```bash
!quality_deals newest
```

_Shows recently added quality game deals_

## 📈 **Benefits**

1. **Real ITAD Approach**: Uses the same data ITAD uses for their "interesting games"
2. **Community Validation**: Games that real people want and own
3. **No Asset Flips**: Comprehensive detection and removal
4. **Always Updated**: Real-time popularity data from ITAD
5. **Multiple Sort Options**: Flexibility like the ITAD website
6. **Smart Filtering**: Quality-first approach with automatic curation

This implementation directly addresses your observation that ITAD shows only interesting games by using their own popularity metrics and community data to achieve the same quality level! 🎉
