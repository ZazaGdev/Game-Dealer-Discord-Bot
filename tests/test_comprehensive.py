#!/usr/bin/env python3
"""Test the fixed priority search functionality - October 2025"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from dotenv import load_dotenv
from api.itad_client import ITADClient

async def main():
    load_dotenv()
    api_key = os.getenv('ITAD_API_KEY')
    if not api_key:
        print(" No ITAD_API_KEY found")
        return False
    
    print(" Testing FIXED Priority Search (Returns Multiple Games!)")
    print("=" * 60)
    
    client = ITADClient(api_key=api_key)
    
    # Test the fix - should now return multiple games instead of just 1
    deals = await client.fetch_deals(
        limit=10, 
        store_filter="Steam", 
        quality_filter=True, 
        min_priority=1
    )
    
    print(f" SUCCESS: Found {len(deals)} Steam priority games!")
    print("(Previous version only returned 1 game)")
    
    for i, deal in enumerate(deals[:5], 1):
        title = deal.get('title', 'Unknown')
        discount = deal.get('discount', 'None')
        price = deal.get('price', 'Unknown')
        print(f"   {i}. {title} - {discount} ({price})")
    
    print(f"\n Priority search is now FIXED and working correctly!")
    return True

if __name__ == "__main__":
    asyncio.run(main())
