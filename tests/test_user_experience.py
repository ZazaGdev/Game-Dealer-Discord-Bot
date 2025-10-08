#!/usr/bin/env python3
"""
Test the actual native_priority command result
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.itad_client import ITADClient
from config.app_config import load_config

async def test_native_priority_results():
    """Test what users actually see from the native_priority command"""
    
    # Initialize client
    config = load_config()
    client = ITADClient(config.itad_api_key)
    
    print("=== TESTING NATIVE PRIORITY RESULTS ===\n")
    
    try:
        # Test the exact scenario users are experiencing
        print("Testing: limit=15, no store filter (default Steam/Epic/GOG)")
        
        results = await client.fetch_native_priority_deals(
            limit=15,
            min_discount=0,
            priority_method="hybrid",
            store_filter=None  # This should trigger default filtering
        )
        
        print(f"\nResults: {len(results)} deals returned")
        print("\nDetailed results:")
        for i, deal in enumerate(results, 1):
            print(f"{i:2d}. {deal['title']}")
            print(f"    {deal.get('discount', 'N/A')} off • {deal['store']} • ${deal['price']}")
            print(f"    {deal['url']}")
            print()
        
        # Test with explicit Steam filter
        print("\n" + "="*50)
        print("Testing: limit=15, explicit Steam filter")
        
        steam_results = await client.fetch_native_priority_deals(
            limit=15,
            min_discount=0,
            priority_method="hybrid",
            store_filter="Steam"
        )
        
        print(f"\nSteam Results: {len(steam_results)} deals returned")
        print("\nSteam detailed results:")
        for i, deal in enumerate(steam_results, 1):
            print(f"{i:2d}. {deal['title']}")
            print(f"    {deal.get('discount', 'N/A')} off • {deal['store']} • ${deal['price']}")
            print()
        
        # Test individual priority methods
        print("\n" + "="*50)
        print("Testing individual priority methods:")
        
        for method in ["popular_deals", "collected_deals", "waitlisted_deals"]:
            print(f"\n--- {method.upper()} ---")
            method_results = await client.fetch_native_priority_deals(
                limit=10,
                min_discount=0,
                priority_method=method,
                store_filter=None
            )
            print(f"Results: {len(method_results)} deals")
            for deal in method_results[:3]:
                print(f"  • {deal['title']} ({deal.get('discount', 'N/A')} off)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_native_priority_results())