# bot/core.py
from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, TYPE_CHECKING
import logging
from utils.embeds import make_startup_embed
from api.itad_client import ITADClient

if TYPE_CHECKING:
    from config.app_config import AppConfig

class GameDealerBot(commands.Bot):
    """Custom Discord bot for GameDealer with enhanced type safety"""
    
    def __init__(self, *, command_prefix: str="!", intents: Optional[discord.Intents]=None,
                 log: Optional[logging.Logger] = None, log_channel_id: int = 0, 
                 deals_channel_id: int = 0, itad_api_key: Optional[str] = None) -> None:
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.log: Optional[logging.Logger] = log
        self.log_channel_id: int = log_channel_id
        self.deals_channel_id: int = deals_channel_id
        self.itad_api_key: Optional[str] = itad_api_key

        # Initialize ITAD client if API key is provided
        self.itad_client: Optional[ITADClient] = None
        if itad_api_key:
            self.itad_client = ITADClient(api_key=itad_api_key)

    async def setup_hook(self) -> None:
        """Initialize bot setup with proper error handling"""
        # Load cogs with individual error handling
        cogs_to_load: List[str] = ["cogs.general", "cogs.deals"]
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                if self.log:
                    self.log.info(f"Successfully loaded {cog}")
            except Exception as e:
                if self.log:
                    self.log.error(f"Failed to load {cog}: {e}")
        
        # List loaded cogs
        if self.log:
            loaded_cogs = [cog.qualified_name for cog in self.cogs.values()]
            self.log.info(f"Loaded cogs: {', '.join(loaded_cogs) if loaded_cogs else 'None'}")
            
        # Sync slash commands to Discord - this makes them appear!
        try:
            synced = await self.tree.sync()
            if self.log:
                self.log.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            if self.log:
                self.log.error(f"Failed to sync commands: {e}")

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Global error handler for commands with proper logging"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"❌ Command `{ctx.invoked_with}` not found. Type `!help` for available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument provided.")
        else:
            if self.log:
                self.log.error(f"Unhandled command error: {error}")
            await ctx.send("❌ An unexpected error occurred.")

    async def close(self) -> None:
        # Close ITAD client
        if self.itad_client:
            await self.itad_client.close()
        # Close the bot
        await super().close()

    # Facade for FastAPI
    async def send_deal(self, deal_data: dict) -> bool:
        cog = self.get_cog("General")
        if not cog:
            if self.log: 
                self.log.error("General cog not loaded; cannot send deal.")
            return False
        return await cog.send_deal_to_discord(deal_data)

# Factory function that main.py expects
def create_bot(*, log: Optional[logging.Logger] = None, log_channel_id: int = 0, deals_channel_id: int = 0, itad_api_key: Optional[str] = None) -> GameDealerBot:
    """Create and return a GameDealerBot instance"""
    return GameDealerBot(
        log=log,
        log_channel_id=log_channel_id,
        deals_channel_id=deals_channel_id,
        itad_api_key=itad_api_key
    )