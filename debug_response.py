# Quick test to capture API response structure
import asyncio
import os
from dotenv import load_dotenv
from api.itad_client import ITADClient

async def capture_response():
    load_dotenv()
    api_key = os.getenv("ITAD_API_KEY")
    
    if not api_key:
        print("No API key found")
        return
    
    print("Attempting to capture API response structure...")
    
    client = ITADClient(api_key=api_key)
    
    try:
        # This will fail due to invalid key, but will capture the error response structure
        deals = await client.fetch_deals(min_discount=10, limit=3)
        print(f"Got {len(deals)} deals")
    except Exception as e:
        print(f"Expected error: {e}")
        print("Check logs/api_responses.json for response structure")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(capture_response())