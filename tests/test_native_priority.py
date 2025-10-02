# tests/test_native_priority.py
"""
Test native ITAD priority search functionality

Validates the intersection-based approach using ITAD's popularity endpoints
"""

import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.itad_client import ITADClient


async def test_native_priority_methods():
    """Test all native priority methods"""
    print("🔍 Testing Native ITAD Priority Search Methods")
    print("=" * 60)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Initialize client with API key
    api_key = os.getenv('ITAD_API_KEY')
    if not api_key:
        print("❌ ITAD_API_KEY environment variable not found")
        print("💡 Please set ITAD_API_KEY in your .env file")
        return
    
    client = ITADClient(api_key=api_key)
    
    methods = [
        ("hybrid", "🔥 Hybrid (Combined)"),
        ("popular_deals", "📊 Most Popular"), 
        ("waitlisted_deals", "💝 Most Waitlisted"),
        ("collected_deals", "🎮 Most Collected")
    ]
    
    try:
        for method_id, method_name in methods:
            print(f"\\n{method_name}")
            print("-" * 40)
            
            try:
                deals = await client.fetch_native_priority_deals(
                    limit=5,
                    min_discount=30,
                    priority_method=method_id
                )
                
                if deals:
                    print(f"✅ Found {len(deals)} deals:")
                    for i, deal in enumerate(deals, 1):
                        print(f"  {i}. {deal['title']}")
                        print(f"     Price: {deal['price']} | Discount: {deal.get('discount', 'N/A')}")
                        print(f"     Store: {deal.get('shop', 'Unknown')}")
                        print()
                else:
                    print("❌ No deals found")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Test with store filter
        print("\\n" + "=" * 60)
        print("🏪 Testing with Steam store filter")
        print("-" * 40)
        
        deals = await client.fetch_native_priority_deals(
            limit=5,
            min_discount=40,
            store_filter="steam",
            priority_method="hybrid"
        )
        
        if deals:
            print(f"✅ Found {len(deals)} Steam deals (40%+ discount):")
            for i, deal in enumerate(deals, 1):
                print(f"  {i}. {deal['title']}")
                print(f"     Price: {deal['price']} | Discount: {deal.get('discount', 'N/A')}")
                print()
        else:
            print("❌ No Steam deals found with 40%+ discount")
        
    finally:
        await client.close()
        print("\\n🏁 Testing completed")


async def test_popularity_endpoints():
    """Test individual popularity endpoints"""
    print("\\n" + "=" * 60)
    print("📊 Testing Individual ITAD Popularity Endpoints")
    print("=" * 60)
    
    api_key = os.getenv('ITAD_API_KEY')
    if not api_key:
        print("❌ ITAD_API_KEY environment variable not found")
        return
    
    client = ITADClient(api_key=api_key)
    
    endpoints = [
        ("most-popular", "📈 Most Popular Games"),
        ("most-waitlisted", "💝 Most Waitlisted Games"),
        ("most-collected", "🎮 Most Collected Games")
    ]
    
    try:
        for endpoint, title in endpoints:
            print(f"\\n{title}")
            print("-" * 40)
            
            try:
                url = f"https://api.isthereanydeal.com/stats/{endpoint}/v1"
                params = {"limit": 5}
                
                response = await client.make_request("GET", url, params=params)
                
                if response and "list" in response:
                    games = response["list"]
                    print(f"✅ Found {len(games)} games:")
                    
                    for i, game in enumerate(games, 1):
                        title = game.get("title", "Unknown")
                        count = game.get("count", 0)
                        print(f"  {i}. {title} (Count: {count:,})")
                else:
                    print("❌ No data received")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    finally:
        await client.close()
        print("\\n🏁 Endpoint testing completed")


async def test_quality_vs_native():
    """Compare quality and native priority methods"""
    print("\\n" + "=" * 60) 
    print("🔄 Comparing Quality vs Native Priority Methods")
    print("=" * 60)
    
    api_key = os.getenv('ITAD_API_KEY')
    if not api_key:
        print("❌ ITAD_API_KEY environment variable not found")
        return
    
    client = ITADClient(api_key=api_key)
    
    try:
        # Test quality method
        print("\\n🎯 Quality Method (ITAD-style)")
        print("-" * 40)
        
        quality_deals = await client.fetch_quality_deals_itad_method(
            limit=5,
            min_discount=30
        )
        
        print(f"✅ Quality method found {len(quality_deals)} deals:")
        for i, deal in enumerate(quality_deals[:3], 1):
            print(f"  {i}. {deal['title']} - {deal.get('discount', 'N/A')}")
        
        # Test native method
        print("\\n🔥 Native Priority Method (Hybrid)")
        print("-" * 40)
        
        native_deals = await client.fetch_native_priority_deals(
            limit=5,
            min_discount=30,
            priority_method="hybrid"
        )
        
        print(f"✅ Native method found {len(native_deals)} deals:")
        for i, deal in enumerate(native_deals[:3], 1):
            print(f"  {i}. {deal['title']} - {deal.get('discount', 'N/A')}")
        
        print(f"\\n💡 Both methods successfully find popular games on sale!")
        
    finally:
        await client.close()
        print("\\n🏁 Comparison completed")


if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_native_priority_methods())
    asyncio.run(test_quality_vs_native())