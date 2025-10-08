# utils/discord_helpers.py
"""
Discord interaction and context handling utilities
"""
import discord
from discord.ext import commands
from typing import Optional, Union, Any, Protocol
import logging

class InteractionLike(Protocol):
    """Protocol for unified interaction/context handling"""
    async def send_message(self, content: Optional[str] = None, embed: Optional[discord.Embed] = None, ephemeral: bool = False) -> None: ...
    async def edit_response(self, content: Optional[str] = None, embed: Optional[discord.Embed] = None) -> None: ...
    async def followup_send(self, content: Optional[str] = None, embed: Optional[discord.Embed] = None) -> None: ...

class InteractionWrapper:
    """Wrapper to provide unified interface for Discord interactions and contexts"""
    
    def __init__(self, interaction_or_ctx: Union[discord.Interaction, commands.Context]):
        self.source = interaction_or_ctx
        self.is_interaction = isinstance(interaction_or_ctx, discord.Interaction)
        self._initial_response_sent = False
    
    async def send_message(self, content: Optional[str] = None, embed: Optional[discord.Embed] = None, ephemeral: bool = False) -> None:
        """Send initial message (works for both interactions and contexts)"""
        try:
            if self.is_interaction:
                if not self._initial_response_sent:
                    await self.source.response.send_message(content=content, embed=embed, ephemeral=ephemeral)
                    self._initial_response_sent = True
                else:
                    await self.source.followup.send(content=content, embed=embed, ephemeral=ephemeral)
            else:
                # Context (prefix command)
                await self.source.send(content=content, embed=embed)
        except discord.NotFound:
            logging.warning("Interaction expired before response could be sent")
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
    
    async def edit_response(self, content: Optional[str] = None, embed: Optional[discord.Embed] = None) -> None:
        """Edit the original response"""
        try:
            if self.is_interaction:
                if self._initial_response_sent:
                    await self.source.edit_original_response(content=content, embed=embed)
                else:
                    # If no initial response sent, send it now
                    await self.send_message(content=content, embed=embed)
            else:
                # For contexts, just send a new message
                await self.source.send(content=content, embed=embed)
        except discord.NotFound:
            logging.warning("Interaction expired before edit could be sent")
        except Exception as e:
            logging.error(f"Failed to edit response: {e}")
    
    async def followup_send(self, content: Optional[str] = None, embed: Optional[discord.Embed] = None, ephemeral: bool = False) -> None:
        """Send a followup message"""
        try:
            if self.is_interaction:
                await self.source.followup.send(content=content, embed=embed, ephemeral=ephemeral)
            else:
                # For contexts, just send a regular message
                await self.source.send(content=content, embed=embed)
        except discord.NotFound:
            logging.warning("Interaction expired before followup could be sent")
        except Exception as e:
            logging.error(f"Failed to send followup: {e}")
    
    async def defer(self, ephemeral: bool = False) -> None:
        """Defer the interaction to prevent timeout"""
        try:
            if self.is_interaction and not self._initial_response_sent:
                await self.source.response.defer(ephemeral=ephemeral)
                self._initial_response_sent = True
        except discord.NotFound:
            logging.warning("Interaction already deferred or expired")
        except Exception as e:
            logging.error(f"Failed to defer interaction: {e}")

class DealDisplayHelper:
    """Helper for displaying deals consistently"""
    
    @staticmethod
    async def display_deals(
        wrapper: InteractionWrapper,
        deals: list,
        title: str,
        use_embeds: bool = True,
        max_per_page: int = 10
    ) -> None:
        """Display deals with consistent formatting"""
        if not deals:
            await wrapper.send_message(f"❌ No deals found for: {title}")
            return
        
        # Split deals into pages if needed
        pages = [deals[i:i + max_per_page] for i in range(0, len(deals), max_per_page)]
        
        for page_num, page_deals in enumerate(pages):
            if use_embeds:
                from utils.embeds import make_deal_embed
                embed = make_deal_embed(page_deals, title)
                
                if page_num == 0:
                    await wrapper.edit_response(embed=embed)
                else:
                    await wrapper.followup_send(embed=embed)
            else:
                # Text-only fallback
                deal_text = f"**{title}**\n\n"
                for i, deal in enumerate(page_deals, 1 + (page_num * max_per_page)):
                    discount_text = f" ({deal.get('discount', 'N/A')} off)" if deal.get('discount') else ""
                    deal_text += f"{i}. **{deal['title']}**{discount_text}\n"
                    deal_text += f"   💰 {deal['price']} • 🏪 {deal['store']}\n"
                    deal_text += f"   🔗 {deal['url']}\n\n"
                
                if page_num == 0:
                    await wrapper.edit_response(content=deal_text)
                else:
                    await wrapper.followup_send(content=deal_text)

def validate_amount(amount: int, max_amount: int = 25) -> tuple[int, Optional[str]]:
    """Validate and normalize deal amount request"""
    if amount < 1:
        return 1, "⚠️ Amount must be at least 1. Set to 1."
    elif amount > max_amount:
        return max_amount, f"⚠️ Amount capped at {max_amount} deals."
    return amount, None

def validate_store_filter(store: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """Validate store filter input"""
    if not store:
        return None, None
    
    # Normalize common store names
    store_mappings = {
        "epic": "Epic Game Store",
        "steam": "Steam", 
        "gog": "GOG",
        "humble": "Humble Store",
        "gmg": "Green Man Gaming",
        "xbox": "Microsoft Store",
        "playstation": "PlayStation Store",
        "nintendo": "Nintendo eShop"
    }
    
    normalized = store_mappings.get(store.lower(), store)
    
    # List of supported stores for validation
    supported_stores = [
        "Steam", "Epic Game Store", "GOG", "Humble Store",
        "Fanatical", "Green Man Gaming", "Microsoft Store",
        "PlayStation Store", "Nintendo eShop", "Battle.net", "itch.io"
    ]
    
    # Check if it's a supported store (case-insensitive)
    for supported in supported_stores:
        if normalized.lower() == supported.lower():
            return supported, None
    
    return store, f"⚠️ Unknown store: {store}. Using anyway, but results may be limited."