#!/usr/bin/env python3
"""
Test script for the new priority search functionality
"""
import asyncio
import json
import os
import sys

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from api.itad_client import ITADClient
from config.app_config import load_config

async def test_new_priority_search():
    """Test the new manual priority search implementation"""
    print("🧪 Testing New Priority Search Implementation")
    print("=" * 60)
    
    # Initialize API client
    config = load_config()
    api_key = config.itad_api_key
    
    if not api_key:
        print("❌ ITAD_API_KEY not found in environment variables")
        return
    
    client = ITADClient(api_key=api_key)
    
    try:
        # Step 1: Load priority games database
        print("📊 Step 1: Loading priority games database...")
        with open('data/priority_games.json', 'r', encoding='utf-8-sig') as f:
            priority_data = json.load(f)
        
        priority_games = priority_data.get('games', [])
        print(f"   Loaded {len(priority_games)} priority games")
        
        # Step 2: Fetch discounted games from ITAD
        print("\n🌐 Step 2: Fetching discounted games from Steam, Epic, GOG...")
        all_deals = []
        
        stores = ["Steam", "Epic Game Store", "GOG"]
        for store in stores:
            try:
                store_deals = await client.fetch_deals(
                    min_discount=1,      # Get all discounted games
                    limit=50,           # Get 50 deals per store
                    store_filter=store,
                    quality_filter=False,  # No filtering yet
                    log_full_response=False
                )
                all_deals.extend(store_deals)
                print(f"   {store}: {len(store_deals)} deals")
            except Exception as e:
                print(f"   ❌ {store}: Error - {e}")
        
        print(f"   Total deals fetched: {len(all_deals)}")
        
        # Step 3: Manual matching with deduplication
        print("\n🎯 Step 3: Matching deals against priority database (with deduplication)...")
        matched_deals = []
        seen_titles = set()  # Track unique titles to prevent duplicates
        min_priority = 5
        min_discount = 10
        
        for deal in all_deals:
            deal_title = deal.get('title', '').strip()
            if not deal_title:
                continue
                
            # Normalize title for duplicate checking
            normalized_title = deal_title.lower().strip()
            
            # Skip if we've already processed this title
            if normalized_title in seen_titles:
                continue
                
            deal_discount = deal.get('discount', '0%')
            
            # Extract discount percentage
            try:
                discount_pct = int(deal_discount.replace('%', ''))
            except (ValueError, AttributeError):
                discount_pct = 0
            
            # Skip if discount doesn't meet minimum
            if discount_pct < min_discount:
                continue
            
            # Find best matching priority game
            best_match = None
            best_match_score = 0
            
            for priority_game in priority_games:
                priority_title = priority_game.get('title', '').lower().strip()
                priority_level = priority_game.get('priority', 0)
                
                # Skip if priority doesn't meet minimum
                if priority_level < min_priority:
                    continue
                
                # Calculate match score
                match_score = 0
                if priority_title == normalized_title:
                    match_score = 1.0  # Exact match
                elif priority_title in normalized_title or normalized_title in priority_title:
                    match_score = 0.8  # Contains match
                
                # Keep track of best match
                if match_score > 0 and (best_match is None or 
                                       priority_level > best_match[0].get('priority', 0) or
                                       (priority_level == best_match[0].get('priority', 0) and match_score > best_match_score)):
                    best_match = (priority_game, match_score)
                    best_match_score = match_score
            
            # If we found a good match, add it and mark title as seen
            if best_match and best_match_score >= 0.8:
                priority_game, match_score = best_match
                
                # Use the priority game's canonical title for deduplication (more reliable)
                canonical_title = priority_game.get('title', '').lower().strip()
                
                # Check if we've already seen this canonical game title
                if canonical_title not in seen_titles:
                    # Mark this canonical title as seen to prevent duplicates
                    seen_titles.add(canonical_title)
                    
                    # Add priority info to deal
                    enhanced_deal = deal.copy()
                    enhanced_deal['_priority'] = priority_game.get('priority', 0)
                    enhanced_deal['_priority_title'] = priority_game.get('title', '')
                    enhanced_deal['_category'] = priority_game.get('category', '')
                    enhanced_deal['_notes'] = priority_game.get('notes', '')
                    enhanced_deal['_match_score'] = match_score
                    enhanced_deal['_discount_pct'] = discount_pct
                    
                    matched_deals.append(enhanced_deal)
        
        print(f"   Unique matches found: {len(matched_deals)} (duplicates removed)")
        print(f"   Duplicate titles processed: {len(seen_titles)} unique titles")
        
        # Step 4: Sort and display results (with 50% discount rule)
        if matched_deals:
            print("\n🏆 Step 4: Top unique priority game deals found:")
            
            def priority_sort_key(deal):
                priority = deal.get('_priority', 0)
                discount = deal.get('_discount_pct', 0)
                
                # If discount > 50%, prioritize by priority score first
                if discount > 50:
                    return (-priority, -discount)  # Higher priority first, then higher discount
                else:
                    return (-discount, -priority)  # Higher discount first, then higher priority
            
            matched_deals.sort(key=priority_sort_key)
            
            for i, deal in enumerate(matched_deals[:10], 1):
                priority = deal.get('_priority', 0)
                category = deal.get('_category', '')
                title = deal.get('_priority_title', deal.get('title', ''))
                discount = deal.get('discount', 'N/A')
                store = deal.get('store', 'Unknown')
                price = deal.get('price', 'N/A')
                
                priority_emoji = "🏆" if priority >= 9 else "⭐" if priority >= 7 else "✨" if priority >= 5 else "🔹"
                
                print(f"   {i:2}. {priority_emoji} {title}")
                print(f"       Priority: {priority}/10 | Category: {category} | {discount} off")
                print(f"       {price} at {store}")
                print()
        else:
            print("   ❌ No matches found with current criteria")
            print(f"      Min Priority: {min_priority}/10")
            print(f"      Min Discount: {min_discount}%")
        
        print("\n✅ New priority search implementation test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_new_priority_search())