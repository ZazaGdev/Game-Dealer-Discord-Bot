import asyncio
from api.itad_client import ITADClient
from dotenv import load_dotenv
import os

async def test():
    load_dotenv()
    client = ITADClient(api_key=os.getenv('ITAD_API_KEY'))
    try:
        # Test store filtering and full response logging
        deals = await client.fetch_deals(min_discount=50, limit=3, store_filter='Epic', log_full_response=True)
        print(f'Found {len(deals)} Epic deals')
        for deal in deals:
            print(f'- {deal["title"]}: {deal["price"]} at {deal["store"]}')
        
        # Test available stores
        stores = client.get_available_stores()
        print(f'Available stores: {stores[:5]}...')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        await client.close()
        
if __name__ == "__main__":
    asyncio.run(test())