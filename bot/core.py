# bot/core.py
from __future__ import annotations
import discord
from discord.ext import commands
from typing import Optional
from utils.embeds import make_startup_embed

class GameDealerBot(commands.Bot):
    def __init__(self, *, command_prefix: str="!", intents: Optional[discord.Intents]=None,
                 log=None, log_channel_id: int=0, deals_channel_id: int=0, itad_api_key: str | None = None):
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.log = log
        self.log_channel_id = log_channel_id
        self.deals_channel_id = deals_channel_id
        self.itad_api_key = itad_api_key

        # Remove ITAD client for now since it's causing import issues
        # self.itad: ITADClient | None = None

    async def setup_hook(self) -> None:
        # Load cogs
        try:
            await self.load_extension("cogs.general")
            if self.log:
                self.log.info("Loaded cogs.general successfully")
        except Exception as e:
            if self.log:
                self.log.error(f"Failed to load cogs.general: {e}")

    async def close(self) -> None:
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
def create_bot(*, log=None, log_channel_id: int = 0, deals_channel_id: int = 0, itad_api_key: str | None = None) -> GameDealerBot:
    """Create and return a GameDealerBot instance"""
    return GameDealerBot(
        log=log,
        log_channel_id=log_channel_id,
        deals_channel_id=deals_channel_id,
        itad_api_key=itad_api_key
    )