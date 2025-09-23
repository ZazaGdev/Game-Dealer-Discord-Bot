#!/usr/bin/env python3
"""
Test the priority search functionality to ensure it only returns priority games
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from api.itad_client import ITADClient


async def test_priority_search():
    """Test priority search functionality"""
    load_dotenv()
    api_key = os.getenv('ITAD_API_KEY')
    
    if not api_key:
        print("❌ No ITAD_API_KEY found")
        return
    
    client = ITADClient(api_key=api_key)
    
    try:
        print("🧪 Testing Priority Search Functionality")
        print("=" * 50)
        
        # Test 1: Strict priority filtering
        print("\n📊 Test 1: Strict priority search (priority 5+, discount 10%+)")
        priority_deals = await client.fetch_deals(
            min_discount=10,
            limit=15,
            quality_filter=True,  # STRICT mode
            min_priority=5
        )
        
        print(f"Found {len(priority_deals)} priority deals:")
        priority_games_found = []
        for i, deal in enumerate(priority_deals[:10], 1):
            priority = deal.get('_priority', 'N/A')
            match_score = deal.get('_match_score', 0)
            title = deal.get('title', 'Unknown')
            discount = deal.get('discount', 'N/A')
            
            # Check if this game is actually in our priority database
            matches = client.priority_filter.find_matching_games(title)
            is_priority = len(matches) > 0 and matches[0][1] >= 0.6
            priority_games_found.append(is_priority)
            
            status = "✅" if is_priority else "❌"
            print(f"  {i:2}. {status} {title[:40]:<40} | P{priority} | {discount} | Score: {match_score:.2f}")
        
        # Verify ALL games are from priority database
        all_priority = all(priority_games_found)
        print(f"\n🎯 Priority filtering verification: {all_priority}")
        if all_priority:
            print("✅ ALL deals are from the priority games database!")
        else:
            non_priority_count = sum(1 for x in priority_games_found if not x)
            print(f"❌ {non_priority_count}/{len(priority_games_found)} deals are NOT from priority database")
        
        # Test 2: Compare with non-priority search
        print(f"\n📊 Test 2: Regular search (no priority filtering)")
        regular_deals = await client.fetch_deals(
            min_discount=10,
            limit=10,
            quality_filter=False  # No filtering
        )
        
        print(f"Found {len(regular_deals)} regular deals:")
        for i, deal in enumerate(regular_deals[:5], 1):
            title = deal.get('title', 'Unknown')
            discount = deal.get('discount', 'N/A')
            
            # Check if this would match our priority database
            matches = client.priority_filter.find_matching_games(title)
            is_priority = len(matches) > 0 and matches[0][1] >= 0.6
            
            status = "🎯" if is_priority else "⚪"
            print(f"  {i:2}. {status} {title[:50]:<50} | {discount}")
        
        # Test 3: High priority games only
        print(f"\n📊 Test 3: High priority games only (priority 8+)")
        high_priority_deals = await client.fetch_deals(
            min_discount=5,
            limit=10,
            quality_filter=True,
            min_priority=8
        )
        
        print(f"Found {len(high_priority_deals)} high priority deals:")
        for i, deal in enumerate(high_priority_deals, 1):
            priority = deal.get('_priority', 'N/A')
            title = deal.get('title', 'Unknown')
            discount = deal.get('discount', 'N/A')
            
            priority_emoji = "🏆" if priority >= 9 else "⭐" if priority >= 7 else "✨"
            print(f"  {i:2}. {priority_emoji} {title[:40]:<40} | P{priority} | {discount}")
        
        print(f"\n📈 Summary:")
        print(f"   Priority deals (5+): {len(priority_deals)}")
        print(f"   Regular deals: {len(regular_deals)}")
        print(f"   High priority deals (8+): {len(high_priority_deals)}")
        print(f"   Priority filtering working: {all_priority}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_priority_search())