# Test script to debug ITAD API integration
import asyncio
import os
from dotenv import load_dotenv
from api.itad_client import ITADClient

async def test_api():
    load_dotenv()
    api_key = os.getenv("ITAD_API_KEY")
    
    print(f"Testing ITAD API v2 with key: {api_key[:10]}...")
    
    client = ITADClient(api_key=api_key)
    
    try:
        deals = await client.fetch_deals(min_discount=30, limit=5)
        print(f"Successfully fetched {len(deals)} deals:")
        for deal in deals:
            print(f"- {deal['title']}: {deal['price']} at {deal['store']} ({deal['discount']})")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_api())