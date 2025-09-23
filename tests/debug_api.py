#!/usr/bin/env python3
"""
Debug script to test why the bot is returning no deals
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from api.itad_client import ITADClient
from utils.game_filters import PriorityGameFilter

async def test_api_and_filtering():
    """Test the API connection and filtering"""
    print("🔍 Debugging GameDealer API Issues")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.getenv('ITAD_API_KEY')
    if not api_key:
        print("❌ No ITAD_API_KEY found in environment variables")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    # Test priority filter loading
    priority_filter = PriorityGameFilter()
    stats = priority_filter.get_database_stats()
    print(f"📊 Priority database: {stats['total_games']} games loaded")
    
    if stats['total_games'] == 0:
        print("❌ Priority database is empty!")
        return False
    
    # Test API connection
    client = ITADClient(api_key=api_key)
    
    try:
        print("\n🌐 Testing API connection...")
        
        # Test with basic fetch first (no filtering)
        print("Testing basic API call without filtering...")
        basic_deals = await client.fetch_deals(
            min_discount=1,
            limit=10,
            quality_filter=False  # No filtering
        )
        
        print(f"📋 Basic API returned: {len(basic_deals)} deals")
        if basic_deals:
            for i, deal in enumerate(basic_deals[:3], 1):
                print(f"  {i}. {deal['title']} - {deal['price']} at {deal['store']}")
        
        # Test with filtering
        print("\n🔍 Testing API call with strict filtering...")
        filtered_deals = await client.fetch_deals(
            min_discount=1,
            limit=10,
            quality_filter=True,
            min_priority=4
        )
        
        print(f"🎯 Filtered API returned: {len(filtered_deals)} deals")
        if filtered_deals:
            for i, deal in enumerate(filtered_deals[:3], 1):
                priority = deal.get('_priority', 'N/A')
                print(f"  {i}. {deal['title']} - {deal['price']} at {deal['store']} (Priority: {priority})")
        else:
            print("❌ No deals passed the priority filter!")
            
            # Let's test the matching manually
            print("\n🔧 Testing manual matching...")
            for deal in basic_deals[:5]:
                matches = priority_filter.find_matching_games(deal['title'])
                print(f"Game: {deal['title']}")
                if matches:
                    best_match = matches[0]
                    print(f"  ✅ Matches: {best_match[0]['title']} (Score: {best_match[1]:.2f}, Priority: {best_match[0]['priority']})")
                else:
                    print(f"  ❌ No matches in priority database")
        
        await client.close()
        return len(filtered_deals) > 0
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        await client.close()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_and_filtering())
    if success:
        print("\n✅ API and filtering working correctly!")
    else:
        print("\n❌ Issues found with API or filtering!")