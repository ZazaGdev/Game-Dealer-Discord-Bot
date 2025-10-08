#!/usr/bin/env python3
"""
Debug script to test ITAD popularity endpoints directly
"""

import asyncio
import aiohttp
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.app_config import load_config

async def test_popularity_endpoints():
    """Test all popularity endpoints to see which ones work"""
    
    # Initialize config
    config = load_config()
    base_url = "https://api.isthereanydeal.com"
    api_key = config.itad_api_key
    
    # Test endpoints with different versions
    endpoints_to_test = [
        # v1 endpoints (current)
        f"{base_url}/stats/most-popular/v1",
        f"{base_url}/stats/most-waitlisted/v1", 
        f"{base_url}/stats/most-collected/v1",
        
        # Try v2 versions 
        f"{base_url}/stats/most-popular/v2",
        f"{base_url}/stats/most-waitlisted/v2",
        f"{base_url}/stats/most-collected/v2",
        
        # Try without version
        f"{base_url}/stats/most-popular",
        f"{base_url}/stats/most-waitlisted",
        f"{base_url}/stats/most-collected",
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_test:
            print(f"\n=== Testing: {endpoint} ===")
            
            params = {
                "key": api_key,
                "limit": 10,
                "offset": 0
            }
            
            try:
                async with session.get(endpoint, params=params) as response:
                    print(f"Status Code: {response.status}")
                    print(f"Headers: {dict(response.headers)}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"Response Type: {type(data)}")
                            if isinstance(data, list):
                                print(f"List Length: {len(data)}")
                                if data:
                                    print(f"First Item Keys: {list(data[0].keys())}")
                                    print(f"First Item: {data[0]}")
                            elif isinstance(data, dict):
                                print(f"Dict Keys: {list(data.keys())}")
                                print(f"Response Data: {data}")
                            else:
                                print(f"Unexpected data type: {type(data)}")
                                print(f"Data: {data}")
                        except Exception as e:
                            text = await response.text()
                            print(f"JSON Parse Error: {e}")
                            print(f"Raw Response: {text[:500]}...")
                    else:
                        text = await response.text()
                        print(f"Error Response: {text[:500]}...")
                        
            except Exception as e:
                print(f"Request Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_popularity_endpoints())