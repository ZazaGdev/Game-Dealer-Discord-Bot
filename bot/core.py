# bot/core.py
from __future__ import annotations
import discord
from discord.ext import commands
from typing import Optional
from utils.embeds import make_startup_embed
from api.itad_client import ITADClient

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

        # Initialize ITAD client if API key is provided
        self.itad_client: ITADClient | None = None
        if itad_api_key:
            self.itad_client = ITADClient(api_key=itad_api_key)

    async def setup_hook(self) -> None:
        # Load cogs
        try:
            await self.load_extension("cogs.general")
            await self.load_extension("cogs.deals")
            if self.log:
                self.log.info("Loaded cogs successfully")
        except Exception as e:
            if self.log:
                self.log.error(f"Failed to load cogs: {e}")

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

    # Add API command directly to the bot class
    @commands.command(name="fetch_deals")
    async def fetch_deals_command(self, ctx: commands.Context, limit: int = 10, min_discount: int = 60):
        """
        Fetch deals with filters directly from bot core
        Usage: !fetch_deals 5 70
        """
        if not self.itad_client:
            await ctx.send("❌ ITAD API not configured. Please check your API key.")
            return

        if limit > 50:
            limit = 50
            await ctx.send("⚠️ Limit capped at 50 deals.")

        await ctx.send(f"🔍 Fetching {limit} deals with minimum {min_discount}% discount...")

        try:
            deals = await self.itad_client.fetch_deals(min_discount=min_discount, limit=limit)
            
            if not deals:
                await ctx.send(f"❌ No deals found with {min_discount}% discount")
                return

            # Send first deal as detailed embed
            if deals:
                from utils.embeds import make_deal_embed
                embed = make_deal_embed(deals[0])
                await ctx.send(f"🎮 **Found {len(deals)} deals!** Here's the best one:", embed=embed)

                # Send summary of other deals
                if len(deals) > 1:
                    summary = "\n".join([
                        f"**{i+2}.** {deal['title'][:40]}{'...' if len(deal['title']) > 40 else ''} - {deal['price']} at {deal['store']}"
                        for i, deal in enumerate(deals[1:6])  # Show next 5
                    ])
                    await ctx.send(f"**Other great deals:**\n{summary}")

        except Exception as e:
            if self.log:
                self.log.error(f"Error fetching deals: {e}")
            await ctx.send("❌ Error occurred while fetching deals.")

# Factory function that main.py expects
def create_bot(*, log=None, log_channel_id: int = 0, deals_channel_id: int = 0, itad_api_key: str | None = None) -> GameDealerBot:
    """Create and return a GameDealerBot instance"""
    return GameDealerBot(
        log=log,
        log_channel_id=log_channel_id,
        deals_channel_id=deals_channel_id,
        itad_api_key=itad_api_key
    )