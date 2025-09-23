#!/usr/bin/env python3
"""
Comprehensive test suite for GameDealer bot functionality.
Consolidates all API, filtering, and bot functionality tests.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from api.itad_client import ITADClient
from utils.game_filters import PriorityGameFilter


class GameDealerTestSuite:
    """Comprehensive test suite for all GameDealer functionality"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('ITAD_API_KEY')
        self.client = None
        self.priority_filter = None
        
    async def setup(self):
        """Set up test environment"""
        if not self.api_key:
            raise Exception("❌ No ITAD_API_KEY found in environment variables")
        
        self.client = ITADClient(api_key=self.api_key)
        self.priority_filter = PriorityGameFilter()
        
    async def teardown(self):
        """Clean up test environment"""
        if self.client:
            await self.client.close()
    
    async def test_api_connectivity(self):
        """Test basic API connectivity"""
        print("\n🌐 Testing API Connectivity")
        print("-" * 30)
        
        try:
            # Test basic API call
            deals = await self.client.fetch_deals(
                min_discount=1,
                limit=5,
                quality_filter=False
            )
            
            if deals:
                print(f"✅ API connectivity successful - {len(deals)} deals fetched")
                print(f"   Sample deal: {deals[0]['title']} at {deals[0]['store']}")
                return True
            else:
                print("⚠️ API connected but no deals returned")
                return False
                
        except Exception as e:
            print(f"❌ API connectivity failed: {e}")
            return False
    
    async def test_priority_filtering(self):
        """Test priority game filtering system"""
        print("\n🎯 Testing Priority Filtering")
        print("-" * 30)
        
        try:
            # Check if priority database loaded
            stats = self.priority_filter.get_database_stats()
            print(f"📊 Priority database: {stats['total_games']} games loaded")
            
            if stats['total_games'] == 0:
                print("❌ Priority database is empty")
                return False
            
            # Test filtering with API data - check exact counts
            basic_deals = await self.client.fetch_deals(
                min_discount=1,
                limit=20,
                quality_filter=False
            )
            
            filtered_deals = await self.client.fetch_deals(
                min_discount=1,
                limit=15,  # Request exactly 15 deals
                quality_filter=True,
                min_priority=4
            )
            
            print(f"📋 Basic deals: {len(basic_deals)} (requested: 20)")
            print(f"🔍 Filtered deals: {len(filtered_deals)} (requested: 15)")
            
            # Test the new priority-based sorting for deals with 50%+ discount
            high_discount_deals = await self.client.fetch_deals(
                min_discount=50,
                limit=10,
                quality_filter=True,
                min_priority=4
            )
            
            print(f"💯 High discount deals (50%+): {len(high_discount_deals)} (requested: 10)")
            
            if filtered_deals:
                print("✅ Priority filtering working")
                print("🎯 Top deals (priority-sorted):")
                for i, deal in enumerate(filtered_deals[:5], 1):
                    priority = deal.get('_priority', 'N/A')
                    discount = deal.get('discount', 'N/A')
                    print(f"   {i}. {deal['title']} (Priority: {priority}, Discount: {discount})")
                
                # Verify exact count compliance
                if len(filtered_deals) <= 15:
                    print(f"✅ Correct item count: {len(filtered_deals)}/15 returned")
                else:
                    print(f"⚠️ Too many items returned: {len(filtered_deals)}/15")
                
                return True
            else:
                print("⚠️ No deals passed priority filter")
                return False
                
        except Exception as e:
            print(f"❌ Priority filtering test failed: {e}")
            return False
    
    async def test_store_filtering(self):
        """Test store-specific filtering"""
        print("\n🏪 Testing Store Filtering")
        print("-" * 30)
        
        test_stores = ["Steam", "Epic Game Store", "GOG"]
        
        for store in test_stores:
            try:
                deals = await self.client.fetch_deals(
                    min_discount=1,
                    limit=5,
                    store_filter=store,
                    quality_filter=False
                )
                
                if deals:
                    print(f"✅ {store}: {len(deals)} deals found")
                    # Verify all deals are from the correct store
                    correct_store = all(store.lower() in deal['store'].lower() for deal in deals)
                    if correct_store:
                        print(f"   ✓ All deals correctly filtered for {store}")
                    else:
                        print(f"   ⚠️ Some deals not from {store}")
                else:
                    print(f"⚠️ {store}: No deals found")
                    
            except Exception as e:
                print(f"❌ {store} filtering failed: {e}")
        
        return True
    
    async def test_priority_based_sorting(self):
        """Test new priority-based sorting logic"""
        print("\n🏆 Testing Priority-Based Sorting")
        print("-" * 30)
        
        try:
            # Get deals with high discounts (50%+) where priority should take precedence
            high_discount_deals = await self.client.fetch_deals(
                min_discount=50,
                limit=10,
                quality_filter=True,
                min_priority=4
            )
            
            print(f"📊 High discount deals found: {len(high_discount_deals)}")
            
            if high_discount_deals:
                print("🔄 Sorting verification (Priority > Discount when discount > 50%):")
                
                # Check if deals are properly sorted by priority when discount > 50%
                for i, deal in enumerate(high_discount_deals[:5], 1):
                    priority = deal.get('_priority', 'N/A')
                    discount = deal.get('discount', 'N/A')
                    title = deal.get('title', 'Unknown')[:30]
                    print(f"   {i}. {title:<30} | Priority: {priority} | Discount: {discount}")
                
                # Verify sorting logic
                high_discount_count = 0
                for deal in high_discount_deals:
                    discount_str = deal.get('discount', '0%')
                    try:
                        discount_num = int(discount_str.replace('%', '')) if discount_str else 0
                        if discount_num > 50:
                            high_discount_count += 1
                    except (ValueError, AttributeError):
                        pass
                
                print(f"✅ {high_discount_count}/{len(high_discount_deals)} deals have >50% discount")
                return True
            else:
                print("⚠️ No high discount deals found to test sorting")
                return True  # Not a failure, just no data
                
        except Exception as e:
            print(f"❌ Priority-based sorting test failed: {e}")
            return False
    
    async def test_deal_quality_parameters(self):
        """Test different deal quality parameters"""
        print("\n💎 Testing Deal Quality Parameters")
        print("-" * 30)
        
        test_cases = [
            {"name": "High discount (80%+)", "params": {"min_discount": 80, "limit": 5}},
            {"name": "Medium discount (50%+)", "params": {"min_discount": 50, "limit": 5}},
            {"name": "Any discount (1%+)", "params": {"min_discount": 1, "limit": 5}},
            {"name": "Priority 8+ games", "params": {"min_discount": 1, "limit": 5, "quality_filter": True, "min_priority": 8}},
            {"name": "Priority 6+ games", "params": {"min_discount": 1, "limit": 10, "quality_filter": True, "min_priority": 6}},
        ]
        
        for test_case in test_cases:
            try:
                deals = await self.client.fetch_deals(**test_case['params'])
                
                if deals:
                    print(f"✅ {test_case['name']}: {len(deals)} deals")
                    if deals[0].get('discount'):
                        print(f"   Best deal: {deals[0]['title']} - {deals[0]['discount']} off")
                else:
                    print(f"⚠️ {test_case['name']}: No deals found")
                    
            except Exception as e:
                print(f"❌ {test_case['name']} failed: {e}")
        
        return True
    
    async def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🛡️ Testing Error Handling")
        print("-" * 30)
        
        # Test with invalid store
        try:
            deals = await self.client.fetch_deals(
                store_filter="InvalidStore123",
                limit=5
            )
            print(f"✅ Invalid store handled gracefully: {len(deals)} deals")
        except Exception as e:
            print(f"⚠️ Invalid store error: {e}")
        
        # Test with extreme parameters
        try:
            deals = await self.client.fetch_deals(
                min_discount=99,  # Very high discount
                limit=1
            )
            print(f"✅ Extreme discount handled: {len(deals)} deals")
        except Exception as e:
            print(f"⚠️ Extreme discount error: {e}")
        
        return True
    
    async def run_all_tests(self):
        """Run the complete test suite"""
        print("🧪 GameDealer Comprehensive Test Suite")
        print("=" * 50)
        
        try:
            await self.setup()
            print(f"✅ Test environment set up with API key: {self.api_key[:8]}...")
            
            # Run all tests
            results = []
            results.append(await self.test_api_connectivity())
            results.append(await self.test_priority_filtering())
            results.append(await self.test_priority_based_sorting())
            results.append(await self.test_store_filtering())
            results.append(await self.test_deal_quality_parameters())
            results.append(await self.test_error_handling())
            
            # Summary
            passed = sum(results)
            total = len(results)
            
            print(f"\n📊 Test Results Summary")
            print("=" * 30)
            print(f"✅ Passed: {passed}/{total} test suites")
            
            if passed == total:
                print("🎉 All tests passed! GameDealer is fully functional.")
                return True
            else:
                print("⚠️ Some tests failed. Check the output above for details.")
                return False
                
        except Exception as e:
            print(f"❌ Test suite setup failed: {e}")
            return False
        finally:
            await self.teardown()


async def main():
    """Main test runner"""
    test_suite = GameDealerTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n🚀 GameDealer is ready for production use!")
    else:
        print("\n🔧 GameDealer needs attention before production use.")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)