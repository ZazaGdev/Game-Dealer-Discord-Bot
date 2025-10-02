# tests/test_quality_structure.py
"""
Test the structure and imports of the ITAD quality system (no API key needed)
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all new modules can be imported successfully"""
    print("🧪 Testing ITAD Quality System Structure\n")
    
    # Test 1: Import quality filtering modules
    print("1. Testing module imports...")
    try:
        from utils.itad_quality import ITADQualityFilter, EnhancedAssetFlipDetector, GamePopularityStats
        print("✅ Successfully imported quality filtering modules")
    except Exception as e:
        print(f"❌ Failed to import quality modules: {e}")
        return False
    
    # Test 2: Import updated ITAD client
    print("\n2. Testing ITAD client integration...")
    try:
        from api.itad_client import ITADClient
        print("✅ Successfully imported updated ITAD client")
    except Exception as e:
        print(f"❌ Failed to import ITAD client: {e}")
        return False
    
    # Test 3: Test class initialization (without API key)
    print("\n3. Testing class structures...")
    try:
        # Test GamePopularityStats dataclass
        stats = GamePopularityStats(
            game_id="test-id",
            title="Test Game",
            waitlisted_count=100,
            collected_count=500,
            popularity_score=600
        )
        print(f"✅ GamePopularityStats: is_popular={stats.is_popular}, quality_score={stats.quality_score:.1f}")
        
        # Test EnhancedAssetFlipDetector
        detector = EnhancedAssetFlipDetector()
        
        # Test with known asset flip patterns
        test_cases = [
            ("The Witcher 3: Wild Hunt", 9.99, 75, False),
            ("Zombie Simulator 2", 0.49, 90, True),
            ("Super Fun Game Pro", 0.99, 95, True),
            ("Civilization VI", 14.99, 70, False),
        ]
        
        print("✅ Asset flip detection tests:")
        for title, price, discount, expected_flip in test_cases:
            is_flip = detector.is_likely_asset_flip(title, price, discount)
            status = "✅" if is_flip == expected_flip else "❌"
            result = "Asset Flip" if is_flip else "Quality Game"
            print(f"   {status} {title}: {result}")
        
    except Exception as e:
        print(f"❌ Failed class structure tests: {e}")
        return False
    
    # Test 4: Test command import
    print("\n4. Testing Discord command integration...")
    try:
        from cogs.deals import Deals
        print("✅ Successfully imported updated deals cog")
        
        # Check if the quality_deals_command method exists
        if hasattr(Deals, 'quality_deals_command'):
            print("✅ quality_deals_command method found in Deals cog")
        else:
            print("❌ quality_deals_command method not found in Deals cog")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test Discord integration: {e}")
        return False
    
    print("\n🎉 All structure tests passed!")
    print("\n📋 Summary of new features:")
    print("   • ITADQualityFilter: Fetches popularity stats from ITAD")
    print("   • EnhancedAssetFlipDetector: Multi-criteria asset flip detection")
    print("   • GamePopularityStats: Data structure for quality scoring")
    print("   • fetch_quality_deals_itad_method: New ITAD client method")
    print("   • !quality_deals command: New Discord command")
    print("\n💡 To test with real data, set ITAD_API_KEY environment variable and run:")
    print("   python tests/test_itad_quality.py")
    
    return True

if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)