#!/usr/bin/env python3
"""
Debug script to test the intersection logic specifically
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.itad_client import ITADClient
from config.app_config import load_config

async def debug_intersection_logic():
    """Debug the intersection matching between popular games and current deals"""
    
    # Initialize client
    config = load_config()
    client = ITADClient(config.itad_api_key)
    
    print("=== DEBUGGING INTERSECTION LOGIC ===\n")
    
    # Test the popular intersection method directly
    try:
        print("1. Testing Popular Intersection Logic:")
        popular_deals = await client._fetch_popular_intersection_deals(
            limit=15, 
            min_discount=0, 
            shop_ids=[61, 16, 35],  # Steam, Epic, GOG
            popularity_type="popular"
        )
        print(f"   Results: {len(popular_deals)} deals found")
        for deal in popular_deals[:5]:
            print(f"   - {deal['title']} ({deal.get('discount', 'N/A')} off on {deal['store']})")
        
        print("\n2. Testing Collected Intersection Logic:")
        collected_deals = await client._fetch_popular_intersection_deals(
            limit=15, 
            min_discount=0, 
            shop_ids=[61, 16, 35],  # Steam, Epic, GOG
            popularity_type="collected"
        )
        print(f"   Results: {len(collected_deals)} deals found")
        for deal in collected_deals[:5]:
            print(f"   - {deal['title']} ({deal.get('discount', 'N/A')} off on {deal['store']})")
            
        print("\n3. Testing Waitlisted Intersection Logic:")
        waitlisted_deals = await client._fetch_popular_intersection_deals(
            limit=15, 
            min_discount=0, 
            shop_ids=[61, 16, 35],  # Steam, Epic, GOG
            popularity_type="waitlisted"
        )
        print(f"   Results: {len(waitlisted_deals)} deals found")
        for deal in waitlisted_deals[:5]:
            print(f"   - {deal['title']} ({deal.get('discount', 'N/A')} off on {deal['store']})")
            
    except Exception as e:
        print(f"Error in intersection logic: {e}")
        import traceback
        traceback.print_exc()
    
    await client.close()

async def debug_intersection_details():
    """Debug the detailed intersection process to see where the bottleneck is"""
    
    # Initialize client
    config = load_config()
    client = ITADClient(config.itad_api_key)
    
    print("\n=== DETAILED INTERSECTION DEBUGGING ===\n")
    
    try:
        # Step 1: Get popular games
        print("Step 1: Fetching popular games...")
        popular_endpoint = f"{client.BASE}/stats/most-popular/v1"
        params = {
            "key": client.api_key,
            "limit": 100,  # Get top 100 popular games
            "offset": 0
        }
        
        popular_data = await client.http.get_json(popular_endpoint, params=params)
        print(f"   Popular games fetched: {len(popular_data)}")
        
        # Build lookup for popular games
        popular_games_data = {}
        for item in popular_data:
            title = item.get("title", "").lower()
            if title:
                popular_games_data[title] = {
                    "id": item.get("id"),
                    "title": item.get("title", ""),
                    "slug": item.get("slug", ""),
                    "count": item.get("count", 0),
                    "position": item.get("position", 999)
                }
        
        print(f"   Popular games lookup built: {len(popular_games_data)} entries")
        print(f"   Sample popular games: {list(popular_games_data.keys())[:5]}")
        
        # Step 2: Get current deals
        print("\nStep 2: Fetching current deals...")
        deals_params = {
            "key": client.api_key,
            "offset": 0,
            "limit": 200,  # Get many deals
            "sort": "-cut",  # Sort by discount
            "nondeals": "false",
            "mature": "false",
            "shops": "61,16,35"  # Steam, Epic, GOG
        }
        
        deals_data = await client.http.get_json(f"{client.BASE}/deals/v2", params=deals_params)
        current_deals = deals_data.get("list", [])
        print(f"   Current deals fetched: {len(current_deals)}")
        
        # Step 3: Test matching process
        print("\nStep 3: Testing title matching...")
        matches_found = 0
        sample_matches = []
        sample_non_matches = []
        
        for deal_item in current_deals[:50]:  # Test first 50 deals
            title = client._get_title_v2(deal_item)
            title_lower = title.lower()
            
            if title_lower in popular_games_data:
                matches_found += 1
                if len(sample_matches) < 5:
                    sample_matches.append(f"'{title}' -> MATCHED")
            else:
                if len(sample_non_matches) < 5:
                    sample_non_matches.append(f"'{title}' -> NO MATCH")
        
        print(f"   Matches found in first 50 deals: {matches_found}")
        print(f"   Sample matches: {sample_matches}")
        print(f"   Sample non-matches: {sample_non_matches}")
        
        # Step 4: Try fuzzy matching for non-matches
        print("\nStep 4: Analyzing match failures...")
        deal_titles = [client._get_title_v2(deal).lower() for deal in current_deals[:20]]
        popular_titles = list(popular_games_data.keys())[:20]
        
        print(f"   Sample deal titles: {deal_titles[:5]}")
        print(f"   Sample popular titles: {popular_titles[:5]}")
        
        # Look for partial matches
        partial_matches = []
        for deal_title in deal_titles[:10]:
            for pop_title in popular_titles[:20]:
                if len(deal_title) > 3 and len(pop_title) > 3:
                    if deal_title in pop_title or pop_title in deal_title:
                        partial_matches.append(f"'{deal_title}' ~ '{pop_title}'")
                        if len(partial_matches) >= 5:
                            break
            if len(partial_matches) >= 5:
                break
        
        print(f"   Partial matches found: {partial_matches}")
        
    except Exception as e:
        print(f"Error in detailed debugging: {e}")
        import traceback
        traceback.print_exc()
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(debug_intersection_logic())
    asyncio.run(debug_intersection_details())