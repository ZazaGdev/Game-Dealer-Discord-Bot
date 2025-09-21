# Test script to test basic ITAD API connectivity
import asyncio
import os
from dotenv import load_dotenv
import aiohttp

async def test_basic_api():
    load_dotenv()
    api_key = os.getenv("ITAD_API_KEY")
    
    print(f"Testing basic ITAD API connectivity...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test a simple search endpoint that should work with API key
            url = "https://api.isthereanydeal.com/games/search/v1"
            params = {
                "key": api_key,
                "title": "cyberpunk",
                "results": 5
            }
            
            async with session.get(url, params=params) as resp:
                print(f"Status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    print(f"Search results: {len(data)} games found")
                    for game in data[:3]:
                        print(f"- {game.get('title', 'Unknown')}")
                else:
                    text = await resp.text()
                    print(f"Error response: {text}")
                    
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_basic_api())