# API Response Templates

This document contains example API response structures for reference when working with the ITAD API.

## ITAD API v2 - Deals Endpoint

### Request

```
GET https://api.isthereanydeal.com/deals/v2
Parameters:
- key: API key
- offset: 0 (pagination)
- limit: number (max 200)
- sort: "-cut" (sort by discount descending)
- nondeals: "false" (only deals)
- mature: "false" (no mature content)
```

### Response Structure

```json
{
  "nextOffset": 3,
  "hasMore": true,
  "list": [
    {
      "id": "game-uuid",
      "slug": "game-slug",
      "title": "Game Title",
      "type": "game",
      "mature": false,
      "assets": {
        "boxart": "url",
        "banner145": "url",
        "banner300": "url",
        "banner400": "url",
        "banner600": "url"
      },
      "deal": {
        "shop": {
          "id": 16,
          "name": "Epic Game Store"
        },
        "price": {
          "amount": 0.00,
          "amountInt": 0,
          "currency": "USD"
        },
        "regular": {
          "amount": 9.99,
          "amountInt": 999,
          "currency": "USD"
        },
        "cut": 100,
        "voucher": null,
        "storeLow": {...},
        "historyLow": {...},
        "flag": "H",
        "drm": [{...}],
        "platforms": [],
        "timestamp": "2025-09-18T17:32:19+02:00",
        "expiry": "2025-09-25T17:00:00+02:00",
        "url": "https://itad.link/..."
      }
    }
  ]
}
```

## Data Extraction Guide

### Store Name

-   Location: `item["deal"]["shop"]["name"]`
-   Example: "Epic Game Store", "Fanatical", "Steam"

### Game Title

-   Location: `item["title"]`
-   Example: "Project Winter"

### Current Price

-   Location: `item["deal"]["price"]["amount"]`
-   Currency: `item["deal"]["price"]["currency"]`
-   Example: 0.00 (free), 1.00, 9.99

### Original Price

-   Location: `item["deal"]["regular"]["amount"]`
-   Example: 9.99

### Discount Percentage

-   Location: `item["deal"]["cut"]`
-   Example: 100 (for 100% off)

### Deal URL

-   Location: `item["deal"]["url"]`
-   Example: "https://itad.link/..."

## Common Store Names

-   Epic Game Store
-   Fanatical
-   Steam
-   GOG
-   Humble Bundle
-   GamesPlanet
-   Green Man Gaming
-   And many more...

## API Key Setup

1. Visit: https://isthereanydeal.com/apps/my/
2. Register your app
3. Get your API key
4. Add to .env file as ITAD_API_KEY=your_key_here

## Error Handling

-   403: Invalid/expired API key
-   404: Endpoint not found
-   429: Rate limit exceeded
-   500: Server error
