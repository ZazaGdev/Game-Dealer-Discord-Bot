#!/usr/bin/env python3
"""
Test the api_responses.json logging functionality
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from api.itad_client import ITADClient


async def test_api_logging():
    """Test that API responses are properly logged"""
    load_dotenv()
    api_key = os.getenv('ITAD_API_KEY')
    
    if not api_key:
        print("❌ No ITAD_API_KEY found")
        return
    
    print("🧪 Testing API Response Logging")
    print("=" * 40)
    
    # Clear existing log file
    log_file = "logs/api_responses.json"
    if os.path.exists(log_file):
        os.remove(log_file)
        print("🗑️  Cleared existing api_responses.json")
    
    client = ITADClient(api_key=api_key)
    
    try:
        # Test 1: Basic API call with logging enabled
        print("\n📝 Test 1: API call with logging enabled")
        deals = await client.fetch_deals(
            min_discount=50,
            limit=5,
            quality_filter=True,
            log_full_response=True  # Enable logging
        )
        
        # Check if log file was created
        if os.path.exists(log_file):
            print("✅ api_responses.json created")
            
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                print(f"📊 Log entries: {len(log_data)}")
                if log_data:
                    latest_entry = log_data[-1]
                    print(f"   Timestamp: {latest_entry['timestamp']}")
                    print(f"   Total items: {latest_entry['response_summary']['total_items']}")
                    print(f"   First 5 deals stored: {len(latest_entry['first_5_deals'])}")
        else:
            print("❌ api_responses.json not created")
        
        # Test 2: Another API call to test appending
        print("\n📝 Test 2: Second API call (should append)")
        deals2 = await client.fetch_deals(
            min_discount=20,
            limit=3,
            store_filter="Steam",
            log_full_response=True
        )
        
        # Check if entries were appended
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                print(f"📊 Log entries after second call: {len(log_data)}")
                if len(log_data) >= 2:
                    print("✅ Entries properly appended")
                    print(f"   Entry 1 store filter: {log_data[0].get('store_filter', 'None')}")
                    print(f"   Entry 2 store filter: {log_data[1].get('store_filter', 'None')}")
                else:
                    print("❌ Entries not properly appended")
        
        # Test 3: API call without logging (should not add entry)
        print("\n📝 Test 3: API call without logging")
        deals3 = await client.fetch_deals(
            min_discount=10,
            limit=2,
            log_full_response=False  # Disable logging
        )
        
        # Check that no new entry was added
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                print(f"📊 Log entries after third call: {len(log_data)}")
                if len(log_data) == 2:
                    print("✅ No entry added when logging disabled")
                else:
                    print("❌ Entry added when logging should be disabled")
        
        print(f"\n🎉 API logging test completed!")
        print(f"   Found {len(deals)} priority deals in test 1")
        print(f"   Found {len(deals2)} Steam deals in test 2") 
        print(f"   Found {len(deals3)} deals in test 3 (no logging)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_api_logging())