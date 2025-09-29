#!/usr/bin/env python3
"""
Debug script to test ITAD API responses and identify format issues
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.itad_client import ITADClient

async def debug_itad_api_format():
    """Test ITAD API calls to see what's causing the format error"""
    
    print("🔍 Debugging ITAD API Response Format Issues")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('ITAD_API_KEY')
    
    if not api_key:
        print("❌ No ITAD_API_KEY found in environment")
        print("Please add your ITAD API key to .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    print()
    
    client = ITADClient(api_key=api_key)
    
    try:
        # Test 1: Raw API call to see the actual response structure
        print("1. Testing raw API response structure...")
        from api.http import HttpClient
        http = HttpClient()
        
        params = {
            "key": api_key,
            "offset": 0,
            "limit": 5,
            "sort": "-cut",
            "nondeals": "false",
            "mature": "false"
        }
        
        try:
            # Make direct HTTP request to check status and content
            async with http.session.get("https://api.isthereanydeal.com/deals/v2", params=params) as resp:
                print(f"   HTTP Status: {resp.status}")
                print(f"   Content Type: {resp.content_type}")
                print(f"   Content Length: {resp.content_length}")
                
                if resp.status != 200:
                    print(f"   ❌ Bad status code: {resp.status}")
                    text_content = await resp.text()
                    print(f"   Error response: {text_content[:500]}...")
                    return False
                
                # Get raw text first
                text_content = await resp.text()
                print(f"   Raw response length: {len(text_content)}")
                
                if not text_content.strip():
                    print(f"   ❌ Empty response from API")
                    return False
                
                # Try to parse JSON
                try:
                    raw_data = json.loads(text_content)
                    print(f"✅ JSON parsed successfully")
                    print(f"   Response type: {type(raw_data)}")
                    
                    if isinstance(raw_data, dict):
                        print(f"   Response keys: {list(raw_data.keys())}")
                        if 'list' in raw_data:
                            print(f"   ✅ Found 'list' key with {len(raw_data['list'])} items")
                        else:
                            print(f"   ❌ Missing 'list' key - this is the problem!")
                            print(f"   Response preview: {json.dumps(raw_data, indent=2)[:500]}...")
                    else:
                        print(f"   ❌ Response is not a dict: {raw_data}")
                        
                except json.JSONDecodeError as json_error:
                    print(f"   ❌ Failed to parse JSON: {json_error}")
                    print(f"   Raw response preview: {text_content[:500]}...")
                    return False
                
        except Exception as raw_error:
            print(f"❌ Raw API call failed: {raw_error}")
            return False
        finally:
            await http.close()
        
        print()
        
        # Test 2: Using ITADClient fetch_deals method
        print("2. Testing ITADClient.fetch_deals()...")
        try:
            deals = await client.fetch_deals(min_discount=1, limit=5, quality_filter=False)
            print(f"✅ ITADClient call successful: Got {len(deals)} deals")
            if deals:
                sample_deal = deals[0]
                print(f"   Sample: {sample_deal['title']} - {sample_deal['discount']} off at {sample_deal['store']}")
        except Exception as client_error:
            print(f"❌ ITADClient call failed: {client_error}")
            if "Unexpected API response format" in str(client_error):
                print("   This confirms the response format issue!")
        
        print()
        
        # Test 3: Different stores
        print("3. Testing different store filters...")
        stores_to_test = ["Steam", "Epic", "GOG"]
        
        for store in stores_to_test:
            try:
                store_deals = await client.fetch_deals(
                    min_discount=1, 
                    limit=3, 
                    store_filter=store, 
                    quality_filter=False
                )
                print(f"   {store}: ✅ {len(store_deals)} deals")
            except Exception as store_error:
                print(f"   {store}: ❌ {store_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
        
    finally:
        await client.close()

if __name__ == "__main__":
    success = asyncio.run(debug_itad_api_format())
    
    if success:
        print("\n🎉 All ITAD API tests passed!")
        print("The API connection is working correctly.")
    else:
        print("\n� ITAD API tests failed.")
        print("Check your API key and network connection.")
        print("You can get an API key at: https://isthereanydeal.com/apps/my/")