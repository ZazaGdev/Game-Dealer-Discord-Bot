# cogs/deals_refactored.py
"""
Refactored deals cog with clean separation of concerns
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Union, List, Any, TYPE_CHECKING
import logging
from utils.discord_helpers import InteractionWrapper
from .deals_core import DealsCommandHandler

if TYPE_CHECKING:
    from api.itad_client import ITADClient

class Deals(commands.Cog):
    """Essential deal commands for GameDealer bot - Refactored for maintainability"""
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.log: Optional[logging.Logger] = getattr(bot, 'log', None)
        self.deals_channel_id: int = getattr(bot, 'deals_channel_id', 0)
        
        # Initialize command handler (will be set when client is available)
        self.handler: Optional[DealsCommandHandler] = None
    
    def _get_handler(self) -> DealsCommandHandler:
        """Get or create the command handler"""
        if self.handler is None:
            client = getattr(self.bot, 'itad_client', None)
            if not client:
                raise RuntimeError("ITAD client not available")
            self.handler = DealsCommandHandler(client, self.log)
        return self.handler

    # =============================================================================
    # GENERAL DEALS COMMANDS
    # =============================================================================
    
    @commands.command(name="search_deals", help="Search for best deals from Steam, Epic, or GOG")
    async def search_deals_prefix(self, ctx: commands.Context, amount: int = 10):
        """Traditional prefix command for searching deals"""
        wrapper = InteractionWrapper(ctx)
        await self._get_handler().search_general_deals(wrapper, amount)

    @app_commands.command(name="search_deals", description="Search for best deals from Steam, Epic, or GOG")
    @app_commands.describe(amount="Number of deals to show (1-25)")
    async def search_deals(self, interaction: discord.Interaction, amount: int = 10):
        """Slash command for searching deals"""
        wrapper = InteractionWrapper(interaction)
        await self._get_handler().search_general_deals(wrapper, amount)

    # =============================================================================
    # STORE-SPECIFIC DEALS COMMANDS
    # =============================================================================
    
    @commands.command(name="search_store", help="Search for deals from a specific store")
    async def search_store_prefix(self, ctx: commands.Context, store: str, amount: int = 10):
        """Traditional prefix command for store-specific deals"""
        wrapper = InteractionWrapper(ctx)
        await self._get_handler().search_store_deals(wrapper, store, amount)

    @app_commands.command(name="search_store", description="Search for deals from a specific store")
    @app_commands.describe(
        store="Store to search (Steam, Epic Game Store, GOG, Xbox, etc.)",
        amount="Number of deals to show (1-25)"
    )
    @app_commands.choices(store=[
        app_commands.Choice(name="Steam", value="Steam"),
        app_commands.Choice(name="Epic Game Store", value="Epic Game Store"),
        app_commands.Choice(name="GOG", value="GOG"),
        app_commands.Choice(name="Xbox/Microsoft Store", value="Xbox"),
        app_commands.Choice(name="Humble Store", value="Humble Store"),
        app_commands.Choice(name="Fanatical", value="Fanatical"),
        app_commands.Choice(name="Green Man Gaming", value="Green Man Gaming"),
        app_commands.Choice(name="PlayStation Store", value="PlayStation Store"),
        app_commands.Choice(name="Nintendo eShop", value="Nintendo eShop"),
    ])
    async def search_deals_by_store(self, interaction: discord.Interaction, store: str, amount: int = 10):
        """Slash command for store-specific deals"""
        wrapper = InteractionWrapper(interaction)
        await self._get_handler().search_store_deals(wrapper, store, amount)

    # =============================================================================
    # PRIORITY DEALS COMMANDS  
    # =============================================================================
    
    @commands.command(name="priority_search", help="Search for priority games with custom filters")
    async def priority_search_prefix(
        self, 
        ctx: commands.Context, 
        amount: int = 10, 
        min_priority: int = 1, 
        min_discount: int = 1, 
        store: str = None
    ):
        """Traditional prefix command for priority deals"""
        wrapper = InteractionWrapper(ctx)
        await self._get_handler().search_priority_deals(wrapper, amount, min_priority, min_discount, store)

    @app_commands.command(name="priority_search", description="Search for priority games with custom filters")
    @app_commands.describe(
        amount="Number of deals to show (1-25)",
        min_priority="Minimum priority level (1-10)",
        min_discount="Minimum discount percentage (0-100)",
        store="Specific store to search (optional)"
    )
    @app_commands.choices(store=[
        app_commands.Choice(name="Steam", value="Steam"),
        app_commands.Choice(name="Epic Game Store", value="Epic Game Store"),
        app_commands.Choice(name="GOG", value="GOG"),
        app_commands.Choice(name="Xbox/Microsoft Store", value="Xbox"),
        app_commands.Choice(name="Humble Store", value="Humble Store"),
        app_commands.Choice(name="Fanatical", value="Fanatical"),
    ])
    async def priority_search_slash(
        self, 
        interaction: discord.Interaction, 
        amount: int = 10, 
        min_priority: int = 1, 
        min_discount: int = 1, 
        store: Optional[str] = None
    ):
        """Slash command for priority deals"""
        wrapper = InteractionWrapper(interaction)
        await self._get_handler().search_priority_deals(wrapper, amount, min_priority, min_discount, store)

    # =============================================================================
    # QUALITY DEALS COMMANDS
    # =============================================================================
    
    @commands.command(name="quality_deals", help="Search for quality deals using enhanced filtering")
    async def quality_deals_prefix(
        self, 
        ctx: commands.Context, 
        amount: int = 10, 
        min_discount: int = 60,
        store: str = None
    ):
        """Traditional prefix command for quality deals"""
        wrapper = InteractionWrapper(ctx)
        await self._get_handler().search_quality_deals(wrapper, amount, min_discount, store)

    @app_commands.command(name="quality_deals", description="Search for quality deals using enhanced filtering")
    @app_commands.describe(
        amount="Number of deals to show (1-25)",
        min_discount="Minimum discount percentage (0-100)",
        store="Specific store to search (optional)"
    )
    @app_commands.choices(store=[
        app_commands.Choice(name="Steam", value="Steam"),
        app_commands.Choice(name="Epic Game Store", value="Epic Game Store"),
        app_commands.Choice(name="GOG", value="GOG"),
        app_commands.Choice(name="Xbox/Microsoft Store", value="Xbox"),
        app_commands.Choice(name="Humble Store", value="Humble Store"),
    ])
    async def quality_deals_slash(
        self, 
        interaction: discord.Interaction, 
        amount: int = 10, 
        min_discount: int = 60,
        store: Optional[str] = None
    ):
        """Slash command for quality deals"""
        wrapper = InteractionWrapper(interaction)
        await self._get_handler().search_quality_deals(wrapper, amount, min_discount, store)

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle command errors gracefully"""
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument: {error}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param}")
        elif isinstance(error, commands.CommandInvokeError):
            if self.log:
                self.log.error(f"Command error in {ctx.command}: {error.original}")
            await ctx.send(f"❌ Command failed: {str(error.original)[:100]}...")
        else:
            if self.log:
                self.log.error(f"Unhandled command error: {error}")
            await ctx.send("❌ An unexpected error occurred.")

async def setup(bot: commands.Bot) -> None:
    """Setup function for loading the cog"""
    await bot.add_cog(Deals(bot))