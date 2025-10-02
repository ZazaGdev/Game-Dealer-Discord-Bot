# tests/test_itad_quality.py
"""
Test the new ITAD quality filtering system
"""

import asyncio
import os
import sys
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.itad_client import ITADClient
from utils.itad_quality import ITADQualityFilter, EnhancedAssetFlipDetector

# Set up basic logging
logging.basicConfig(level=logging.INFO)

async def test_quality_system():
    """Test the ITAD quality filtering system"""
    
    # Load API key
    api_key = os.getenv("ITAD_API_KEY")
    if not api_key:
        print("❌ ITAD_API_KEY environment variable not set")
        return
    
    print("🧪 Testing ITAD Quality Filtering System\n")
    
    # Test 1: Initialize ITAD client with quality filtering
    print("1. Testing ITAD Client with Quality Filtering...")
    try:
        client = ITADClient(api_key=api_key)
        print("✅ ITAD Client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize ITAD client: {e}")
        return
    
    # Test 2: Test standalone quality filter
    print("\n2. Testing Standalone Quality Filter...")
    try:
        quality_filter = ITADQualityFilter(api_key)
        popular_games = await quality_filter.get_popular_games_stats(limit=100)
        print(f"✅ Loaded popularity stats for {len(popular_games)} games")
        
        # Show some examples
        sample_games = list(popular_games.items())[:5]
        for title, stats in sample_games:
            print(f"   📊 {stats.title}: waitlisted={stats.waitlisted_count}, collected={stats.collected_count}, quality_score={stats.quality_score:.1f}")
            
    except Exception as e:
        print(f"❌ Failed to test quality filter: {e}")
    
    # Test 3: Test asset flip detector
    print("\n3. Testing Enhanced Asset Flip Detector...")
    try:
        detector = EnhancedAssetFlipDetector()
        
        # Test cases
        test_games = [
            ("The Witcher 3: Wild Hunt", 9.99, 75),  # Should NOT be asset flip
            ("Cyberpunk 2077", 29.99, 50),           # Should NOT be asset flip
            ("Zombie Simulator 2", 0.49, 90),        # Should be asset flip
            ("Super Fun Game Pro", 0.99, 95),        # Should be asset flip
            ("Civilization VI", 14.99, 70),          # Should NOT be asset flip
        ]
        
        for title, price, discount in test_games:
            is_asset_flip = detector.is_likely_asset_flip(title, price, discount)
            status = "🚫 Asset Flip" if is_asset_flip else "✅ Quality Game"
            print(f"   {status}: {title} (${price}, {discount}% off)")
            
    except Exception as e:
        print(f"❌ Failed to test asset flip detector: {e}")
    
    # Test 4: Test the new quality deals method
    print("\n4. Testing ITAD Quality Deals Method...")
    try:
        deals = await client.fetch_quality_deals_itad_method(
            limit=5,
            min_discount=30,
            sort_by="hottest",
            use_popularity_stats=True
        )
        
        print(f"✅ Found {len(deals)} quality deals:")
        for i, deal in enumerate(deals, 1):
            print(f"   {i}. {deal['title']} - {deal['price']} ({deal['discount']}) on {deal['store']}")
            
    except Exception as e:
        print(f"❌ Failed to test quality deals method: {e}")
    
    # Test 5: Compare different sorting methods
    print("\n5. Testing Different Sorting Methods...")
    try:
        sort_methods = ["hottest", "discount", "price"]
        
        for sort_method in sort_methods:
            deals = await client.fetch_quality_deals_itad_method(
                limit=3,
                min_discount=40,
                sort_by=sort_method,
                use_popularity_stats=True
            )
            
            print(f"   📈 {sort_method.title()} Sort ({len(deals)} deals):")
            for deal in deals:
                print(f"      • {deal['title']} - {deal['price']} ({deal['discount']})")
                
    except Exception as e:
        print(f"❌ Failed to test sorting methods: {e}")
    
    # Cleanup
    await client.close()
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    asyncio.run(test_quality_system())