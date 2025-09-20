from __future__ import annotations
import logging
import discord
from discord.ext import commands
from typing import Optional, Any


class GameDealerBot(commands.Bot):
    """
    Central Discord client for GameDealer.
    - attaches logging + channel ids
    - auto-loads cogs
    - exposes a small API (send_deal) that main.py / FastAPI can call
    """
    def __init__(
        self,
        *,
        command_prefix: str = "!",
        intents: Optional[discord.Intents] = None,
        log: Optional[logging.Logger] = None,
        log_channel_id: int = 0,
        deals_channel_id: int = 0,
    ):
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True

        super().__init__(command_prefix=command_prefix, intents=intents)

        # shared state
        self.log = log
        self.log_channel_id = log_channel_id
        self.deals_channel_id = deals_channel_id

    async def setup_hook(self) -> None:
        """Load cogs/extensions before the bot becomes ready."""
        # you can add more cogs here later (e.g., "cogs.deals", "cogs.admin")
        await self.load_extension("cogs.general")

    # --- Small public API for the rest of the app ---
    async def send_deal(self, deal_data: dict) -> bool:
        """Proxy to the cog's method, safe to call from outside."""
        cog = self.get_cog("General")
        if not cog:
            if self.log:
                self.log.error("General cog not loaded; cannot send deal.")
            return False
        return await cog.send_deal_to_discord(deal_data)


def create_bot(*, log, log_channel_id: int, deals_channel_id: int) -> GameDealerBot:
    """Factory used by main.py, keeps wiring in one place."""
    intents = discord.Intents.default()
    intents.message_content = True
    return GameDealerBot(
        command_prefix="!",
        intents=intents,
        log=log,
        log_channel_id=log_channel_id,
        deals_channel_id=deals_channel_id,
    )
