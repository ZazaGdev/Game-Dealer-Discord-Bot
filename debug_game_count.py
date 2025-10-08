"""
Debug why native priority is only returning 3 games
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.insert(0, '.')

from api.itad_client import ITADClient


async def debug_game_count():
    """Debug why we're only getting 3 games"""
    print("🔍 Debugging Game Count Issue")
    print("=" * 50)
    
    api_key = os.getenv('ITAD_API_KEY')
    if not api_key:
        print("❌ ITAD_API_KEY not found")
        return
    
    client = ITADClient(api_key=api_key)
    
    try:
        # Test with different limits to see what's happening
        for limit in [5, 10, 15, 20]:
            print(f"\n🎯 Testing with limit={limit}:")
            
            deals = await client.fetch_native_priority_deals(
                limit=limit,
                min_discount=20,  # Lower discount to get more results
                store_filter=None,  # Use default stores
                priority_method="hybrid"
            )
            
            print(f"   Requested: {limit}, Got: {len(deals)}")
            
            if deals:
                for i, deal in enumerate(deals[:3], 1):
                    title = deal['title'][:40] + "..." if len(deal['title']) > 40 else deal['title']
                    discount = deal.get('discount', 'N/A')
                    print(f"      {i}. {title} - {discount}")
                if len(deals) > 3:
                    print(f"      ... and {len(deals) - 3} more")
        
        # Let's also test the individual methods that make up hybrid
        print(f"\n🔍 Testing individual priority methods:")
        
        methods = [
            ("popular_deals", "📊 Popular"),
            ("waitlisted_deals", "💝 Waitlisted"), 
            ("collected_deals", "🎮 Collected")
        ]
        
        for method_id, method_name in methods:
            deals = await client.fetch_native_priority_deals(
                limit=10,
                min_discount=20,
                store_filter=None,
                priority_method=method_id
            )
            print(f"   {method_name}: {len(deals)} deals")
        
        # Let's check what the raw deals API returns
        print(f"\n🌐 Testing raw deals API (Steam + Epic + GOG):")
        
        # Get shop IDs
        steam_id = client._get_shop_id("steam")
        epic_id = client._get_shop_id("epic") 
        gog_id = client._get_shop_id("gog")
        
        for store_name, shop_id in [("Steam", steam_id), ("Epic", epic_id), ("GOG", gog_id)]:
            if shop_id:
                try:
                    url = "https://api.isthereanydeal.com/deals/v2"
                    params = {
                        "key": api_key,
                        "limit": 20,
                        "shops": str(shop_id),
                        "offset": 0
                    }
                    
                    response = await client.http.get_json(url, params=params)
                    
                    if response and 'list' in response:
                        deals_count = len(response['list'])
                        print(f"   {store_name} (ID {shop_id}): {deals_count} raw deals available")
                    else:
                        print(f"   {store_name} (ID {shop_id}): No deals found")
                        
                except Exception as e:
                    print(f"   {store_name} (ID {shop_id}): Error - {e}")
        
        # Test combined shop IDs
        print(f"\n🔗 Testing combined shop IDs:")
        try:
            url = "https://api.isthereanydeal.com/deals/v2"
            params = {
                "key": api_key,
                "limit": 50,
                "shops": f"{steam_id},{epic_id},{gog_id}",  # Combined
                "offset": 0
            }
            
            response = await client.http.get_json(url, params=params)
            
            if response and 'list' in response:
                deals_count = len(response['list'])
                print(f"   Combined Steam+Epic+GOG: {deals_count} raw deals available")
                
                # Show sample of what's available
                if response['list']:
                    print(f"   Sample deals:")
                    for i, deal in enumerate(response['list'][:5], 1):
                        title = deal.get('title', 'Unknown')[:30] + "..."
                        shop_info = deal.get('shop', {})
                        print(f"      {i}. {title}")
            else:
                print(f"   Combined: No deals found")
                
        except Exception as e:
            print(f"   Combined: Error - {e}")
        
        # Test popularity endpoints to see how many popular games we get
        print(f"\n📊 Testing popularity endpoints:")
        
        popularity_endpoints = [
            ("most-popular", "Most Popular"),
            ("most-waitlisted", "Most Waitlisted"),
            ("most-collected", "Most Collected")
        ]
        
        for endpoint, name in popularity_endpoints:
            try:
                url = f"https://api.isthereanydeal.com/stats/{endpoint}/v1"
                params = {"limit": 500}  # Max we request
                
                response = await client.http.get_json(url, params=params)
                
                if response and 'list' in response:
                    games_count = len(response['list'])
                    print(f"   {name}: {games_count} games available")
                else:
                    print(f"   {name}: No data")
                    
            except Exception as e:
                print(f"   {name}: Error - {e}")
        
    finally:
        await client.close()
        print(f"\n🏁 Debug completed!")


if __name__ == "__main__":
    asyncio.run(debug_game_count())