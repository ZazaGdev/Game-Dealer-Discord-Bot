# Native ITAD Priority Search - Command Guide

## 🔥 New Commands Available

### 1. Native Priority Search

**Command:** `!native_priority` (aliases: `!np`, `!native`, `!itad_priority`)

**Description:** Uses ITAD's native popularity endpoints to find the best deals for games people actually want and play.

**Usage:**

```
!native_priority [method] [store] [min_discount]
```

**Examples:**

```bash
!native_priority                      # Default: hybrid method, 30% minimum discount
!native_priority hybrid steam 40      # Steam deals only, 40%+ discount
!np popular_deals                     # Most popular games method
!native waitlisted_deals epic 50      # Most waitlisted games on Epic, 50%+ discount
!itad_priority collected_deals gog 25 # Most collected games on GOG, 25%+ discount
```

**Methods Available:**

-   `hybrid` - 🔥 **Recommended** - Combines all popularity sources for best results
-   `popular_deals` - 📊 Uses ITAD's most-popular games endpoint
-   `waitlisted_deals` - 💝 Uses ITAD's most-waitlisted games endpoint
-   `collected_deals` - 🎮 Uses ITAD's most-collected games endpoint

**Parameters:**

-   `method` - Priority calculation method (default: hybrid)
-   `store` - Store filter: Steam, Epic, GOG (optional)
-   `min_discount` - Minimum discount percentage (default: 30)

---

### 2. Priority Method Comparison

**Command:** `!priority_comparison` (aliases: `!pc`, `!compare_priority`)

**Description:** Compare results from different ITAD priority methods side-by-side.

**Usage:**

```
!priority_comparison [store] [min_discount]
```

**Examples:**

```bash
!priority_comparison                  # Compare all methods, 40%+ discount
!pc steam 50                         # Compare Steam deals, 50%+ discount
!compare_priority gog 30             # Compare GOG deals, 30%+ discount
```

Shows top 3 results from each method:

-   🔥 Hybrid (Recommended)
-   📊 Most Popular
-   💝 Most Waitlisted
-   🎮 Most Collected

---

### 3. Quality Deals (Enhanced)

**Command:** `!quality_deals` (aliases: `!quality`, `!q`, `!interesting`)

**Description:** ITAD-style "interesting games" using popularity data and asset flip detection.

**Usage:**

```
!quality_deals [store] [min_discount] [sort]
```

**Examples:**

```bash
!quality_deals                       # Default: 50% discount, hottest sort
!quality steam 60 newest            # Steam deals, 60%+ discount, newest first
!q gog 40 discount                  # GOG deals, 40%+ discount, by discount %
```

---

## 🎯 How Native Priority Works

### The Problem

-   Traditional priority search relied on local JSON database
-   Limited to manually curated games
-   Didn't scale with new releases or changing popularity

### The Solution

Native ITAD Priority uses **intersection-based approach**:

1. **Fetch Popular Games** - Gets ITAD's community-validated popular games
2. **Find Current Deals** - Gets all current deals from ITAD deals API
3. **Smart Matching** - Uses fuzzy title matching to find popular games on sale
4. **Priority Ranking** - Ranks by popularity scores + discount percentages

### Popularity Sources

-   **Most Popular** - Games currently trending on ITAD
-   **Most Waitlisted** - Games people want but don't own yet
-   **Most Collected** - Games people actually own and play
-   **Hybrid** - Weighted combination of all three for balanced results

---

## 📊 Comparison: Native vs Quality vs Original

| Method                | Source                                 | Best For                              | Database    |
| --------------------- | -------------------------------------- | ------------------------------------- | ----------- |
| **Native Priority**   | ITAD popularity APIs                   | Popular games currently on sale       | None needed |
| **Quality Deals**     | ITAD popularity + asset flip detection | "Interesting" games like ITAD website | None needed |
| **Original Priority** | Local priority_games.json              | Manually curated favorites            | Local file  |

---

## 🚀 Quick Start

1. **Best Overall Results:**

    ```bash
    !native_priority hybrid
    ```

2. **Steam-Only Popular Games:**

    ```bash
    !np hybrid steam 40
    ```

3. **Compare All Methods:**

    ```bash
    !priority_comparison steam
    ```

4. **Quality "Interesting" Games:**
    ```bash
    !quality_deals steam 50
    ```

---

## 🔧 Technical Details

### API Endpoints Used

-   `https://api.isthereanydeal.com/stats/most-popular/v1`
-   `https://api.isthereanydeal.com/stats/most-waitlisted/v1`
-   `https://api.isthereanydeal.com/stats/most-collected/v1`
-   `https://api.isthereanydeal.com/deals/v2`

### Fuzzy Matching

Uses Python's `fuzzywuzzy` library with 80% similarity threshold for matching game titles between popularity lists and current deals.

### Performance

-   Fetches up to 500 popular games per method
-   Processes deals in batches for efficiency
-   Smart caching to avoid repeated API calls

### Error Handling

-   Validates all user inputs
-   Graceful fallback for API failures
-   Informative error messages with suggestions

---

## 💡 Pro Tips

1. **Hybrid method** generally gives the best balanced results
2. Use **popular_deals** for currently trending games
3. Use **waitlisted_deals** for games people want but haven't bought
4. Use **collected_deals** for proven classics people actually play
5. **Quality deals** best for discovering interesting games you might miss
6. **Comparison command** helps you see different perspectives on what's popular

---

## 🎮 Example Results

**Hybrid Method Output:**

```
🔥 Native ITAD Priority Deals (Hybrid)
Combined popularity sources (most-popular + most-waitlisted + most-collected)
Showing 3 deals (40%+ discount)

1. XCOM 2 - $2.99 (95% off) - Steam
2. Nightingale - Free (100% off) - Epic
3. Lords of the Fallen™ (2014) GOTY - $1.49 (95% off) - Steam
```

**Priority Comparison Output:**

```
🎯 ITAD Priority Methods Comparison
Filters: 40%+ discount, Steam only

🔥 Hybrid (Recommended) (2 deals)
1. XCOM 2 - $2.99 (95%)
2. Lords of the Fallen™ GOTY - $1.49 (95%)

📊 Most Popular (1 deals)
1. XCOM 2 - $2.99 (95%)

💝 Most Waitlisted (1 deals)
1. Nightingale - Free (100%)

🎮 Most Collected (1 deals)
1. XCOM 2 - $2.99 (95%)
```
