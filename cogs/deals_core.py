# cogs/deals_core.py
"""
Core deal command logic separated from Discord interaction handling
"""
from typing import List, Optional, Union, TYPE_CHECKING
import logging
from models import Deal, StoreFilter
from utils.discord_helpers import InteractionWrapper, DealDisplayHelper, validate_amount, validate_store_filter

if TYPE_CHECKING:
    from api.itad_client import ITADClient

class DealsCommandHandler:
    """Handles the core logic for deal commands, separated from Discord-specific code"""
    
    def __init__(self, client: 'ITADClient', logger: Optional[logging.Logger] = None):
        self.client = client
        self.logger = logger or logging.getLogger(__name__)
    
    async def search_general_deals(
        self,
        wrapper: InteractionWrapper,
        amount: int = 10,
        min_discount: int = 60
    ) -> None:
        """
        Search for general deals from default stores (Steam, Epic, GOG)
        """
        # Validate amount
        amount, warning = validate_amount(amount)
        if warning:
            await wrapper.send_message(warning)
        
        # Show searching message
        await wrapper.send_message(f"🔍 Searching for {amount} best deals from Steam, Epic & GOG...")
        
        try:
            # Fetch deals from API
            deals = await self.client.fetch_deals(
                min_discount=min_discount,
                limit=amount,
                store_filter=None,  # Use default stores
                quality_filter=True,
                min_priority=5
            )
            
            # Display results
            title = f"🎮 Top {len(deals)} Gaming Deals (≥{min_discount}% off)"
            await DealDisplayHelper.display_deals(wrapper, deals, title)
            
            self.logger.info(f"Returned {len(deals)} general deals")
            
        except Exception as e:
            self.logger.error(f"Failed to fetch general deals: {e}")
            await wrapper.edit_response(
                content=f"❌ Failed to fetch deals: {str(e)[:100]}..."
            )
    
    async def search_store_deals(
        self,
        wrapper: InteractionWrapper,
        store: str,
        amount: int = 10,
        min_discount: int = 60
    ) -> None:
        """
        Search for deals from a specific store
        """
        # Validate inputs
        amount, amount_warning = validate_amount(amount)
        store_filter, store_warning = validate_store_filter(store)
        
        # Send warnings if any
        warnings = []
        if amount_warning:
            warnings.append(amount_warning)
        if store_warning:
            warnings.append(store_warning)
        
        if warnings:
            await wrapper.send_message("\n".join(warnings))
        
        # Show searching message
        await wrapper.send_message(f"🔍 Searching for {amount} deals from {store_filter or store}...")
        
        try:
            # Fetch deals from specific store
            deals = await self.client.fetch_deals(
                min_discount=min_discount,
                limit=amount,
                store_filter=store_filter or store,
                quality_filter=True,
                min_priority=5
            )
            
            # Display results
            title = f"🏪 {store_filter or store} Deals (≥{min_discount}% off)"
            await DealDisplayHelper.display_deals(wrapper, deals, title)
            
            self.logger.info(f"Returned {len(deals)} deals from {store}")
            
        except Exception as e:
            self.logger.error(f"Failed to fetch store deals for {store}: {e}")
            await wrapper.edit_response(
                content=f"❌ Failed to fetch {store} deals: {str(e)[:100]}..."
            )
    
    async def search_priority_deals(
        self,
        wrapper: InteractionWrapper,
        amount: int = 10,
        min_priority: int = 1,
        min_discount: int = 1,
        store: Optional[str] = None
    ) -> None:
        """
        Search for priority deals based on user preferences
        """
        # Validate inputs
        amount, amount_warning = validate_amount(amount)
        store_filter, store_warning = validate_store_filter(store) if store else (None, None)
        
        # Send warnings
        warnings = []
        if amount_warning:
            warnings.append(amount_warning)
        if store_warning:
            warnings.append(store_warning)
        
        if warnings:
            await wrapper.send_message("\n".join(warnings))
        
        # Show searching message
        store_text = f" from {store_filter or store}" if store else ""
        await wrapper.send_message(
            f"🎯 Searching for {amount} priority deals{store_text} "
            f"(priority≥{min_priority}, discount≥{min_discount}%)..."
        )
        
        try:
            # Fetch priority deals
            deals = await self.client.fetch_deals(
                min_discount=min_discount,
                limit=amount,
                store_filter=store_filter or store,
                quality_filter=True,
                min_priority=min_priority
            )
            
            # Display results
            title = f"🎯 Priority Deals (P≥{min_priority}, D≥{min_discount}%)"
            if store_filter or store:
                title += f" - {store_filter or store}"
            
            await DealDisplayHelper.display_deals(wrapper, deals, title)
            
            self.logger.info(f"Returned {len(deals)} priority deals")
            
        except Exception as e:
            self.logger.error(f"Failed to fetch priority deals: {e}")
            await wrapper.edit_response(
                content=f"❌ Failed to fetch priority deals: {str(e)[:100]}..."
            )
    
    async def search_quality_deals(
        self,
        wrapper: InteractionWrapper,
        amount: int = 10,
        min_discount: int = 60,
        store: Optional[str] = None
    ) -> None:
        """
        Search for quality deals using enhanced filtering
        """
        # Validate inputs
        amount, amount_warning = validate_amount(amount)
        store_filter, store_warning = validate_store_filter(store) if store else (None, None)
        
        # Send warnings
        warnings = []
        if amount_warning:
            warnings.append(amount_warning)
        if store_warning:
            warnings.append(store_warning)
        
        if warnings:
            await wrapper.send_message("\n".join(warnings))
        
        # Show searching message
        store_text = f" from {store_filter or store}" if store else ""
        await wrapper.send_message(f"✨ Searching for {amount} quality deals{store_text}...")
        
        try:
            # Fetch quality deals using ITAD's quality system
            deals = await self.client.fetch_quality_deals_itad_method(
                limit=amount,
                min_discount=min_discount,
                store_filter=store_filter or store
            )
            
            # Display results
            title = f"✨ Quality Deals (≥{min_discount}% off)"
            if store_filter or store:
                title += f" - {store_filter or store}"
            
            await DealDisplayHelper.display_deals(wrapper, deals, title)
            
            self.logger.info(f"Returned {len(deals)} quality deals")
            
        except Exception as e:
            self.logger.error(f"Failed to fetch quality deals: {e}")
            await wrapper.edit_response(
                content=f"❌ Failed to fetch quality deals: {str(e)[:100]}..."
            )