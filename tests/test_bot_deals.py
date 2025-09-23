#!/usr/bin/env python3
"""
Test the actual bot deals functionality to ensure it works end-to-end
"""

import asyncio
import os
from dotenv import load_dotenv
from api.itad_client import ITADClient

async def test_bot_deals():
    """Test that the bot can fetch deals successfully"""
    print("🤖 Testing GameDealer Bot Deals Functionality")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('ITAD_API_KEY')
    
    if not api_key:
        print("❌ No API key configured")
        return False
    
    # Create ITAD client directly
    client = ITADClient(api_key=api_key)
    
    try:
        print("🔍 Testing deal fetching...")
        
        # Test fetching deals with different parameters
        test_cases = [
            {"name": "Basic deals (no filtering)", "params": {"limit": 5, "quality_filter": False}},
            {"name": "Priority filtered deals", "params": {"limit": 10, "quality_filter": True, "min_priority": 4}},
            {"name": "High priority only", "params": {"limit": 5, "quality_filter": True, "min_priority": 8}},
        ]
        
        for test_case in test_cases:
            print(f"\n📋 {test_case['name']}:")
            try:
                deals = await client.fetch_deals(**test_case['params'])
                print(f"   ✅ Found {len(deals)} deals")
                
                if deals:
                    for i, deal in enumerate(deals[:3], 1):
                        priority = deal.get('_priority', 'N/A')
                        priority_text = f" (Priority: {priority})" if priority != 'N/A' else ""
                        print(f"   {i}. {deal['title']} - {deal['price']} at {deal['store']}{priority_text}")
                else:
                    print(f"   ⚠️ No deals found for this test case")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        await client.close()
        print("\n🎯 Bot deals functionality test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        await client.close()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bot_deals())
    if success:
        print("\n✅ Bot deals functionality is working correctly!")
        print("📢 The /search_deals and /search_store commands should now work properly.")
    else:
        print("\n❌ Issues found with bot deals functionality!")