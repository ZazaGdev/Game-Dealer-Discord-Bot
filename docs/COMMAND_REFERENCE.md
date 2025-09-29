# GameDealer Bot - Command Reference

## Command Types

-   **Slash Commands**: `/command` (modern, autocomplete)
-   **Prefix Commands**: `!command` (traditional text-based)

## Deal Commands

### `/search_deals [amount]` | `!search_deals [amount]`

**Purpose**: Best deals from Steam, Epic, GOG
**Parameters**:

-   `amount` (optional): Integer, 1-25, default 10
    **Examples**: `/search_deals amount:15` | `!search_deals 15`

### `/search_store store:[name] [amount]` | `!search_store [name] [amount]`

**Purpose**: Deals from specific store
**Parameters**:

-   `store` (required): String, store name (Steam, Epic, GOG, etc.)
-   `amount` (optional): Integer, 1-25, default 10
    **Examples**: `/search_store store:Steam amount:20` | `!search_store Steam 20`

### `/priority_search [amount] [min_priority] [min_discount] [store]` | `!priority_search [amount] [min_priority] [min_discount] [store]`

**Purpose**: Curated priority games only with EXACT matching (prevents false positives)
**Parameters**:

-   `amount` (optional): Integer, 1-25, default 10
-   `min_priority` (optional): Integer, 1-10, default 5 (Priority scale: 1-3 low, 4-6 medium, 7-8 high, 9-10 premium)
-   `min_discount` (optional): Integer, 1-100%, default 1
-   `store` (optional): String, store name or searches all if omitted
    **Matching**: Exact title matching only (ignores ™®© symbols), prevents "Raft" from matching "Minecraft: Raft Edition"
    **Examples**:
-   `/priority_search amount:15 min_priority:8 min_discount:50 store:Steam`
-   `!priority_search 15 8 50 Steam`

## Utility Commands

### `/ping`

**Purpose**: Test bot responsiveness
**Parameters**: None
**Response**: Latency in milliseconds

### `/info`

**Purpose**: Bot information and statistics
**Parameters**: None
**Shows**: Database size, supported stores, latency, server/user counts

### `/help`

**Purpose**: Display available commands
**Parameters**: None
**Shows**: Command list with examples

## Validation & Indicators

**Auto-validation**: amount (max 25), min_priority (1-10), min_discount (1-100%), store (partial match)
**Priority**: 🏆 Premium (9-10) | ⭐ High (7-8) | ✨ Good (5-6) | 📦 Standard (1-4)

## Common Usage

-   Browse: `/search_deals amount:25` | Store: `/search_store store:Steam amount:20`
-   Quality: `/priority_search min_priority:8 min_discount:50` | Compare stores with different store parameters
