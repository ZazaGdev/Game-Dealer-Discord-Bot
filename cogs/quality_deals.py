# cogs/quality_deals.py
"""
Quality Deals Discord Cog

Implements the !quality_deals command using ITAD's approach to show interesting games
"""

import logging
from typing import Optional

import discord
from discord.ext import commands

from api.itad_client import ITADClient
from utils.embeds import create_deals_embed, create_error_embed, create_no_deals_embed


class QualityDeals(commands.Cog):
    """Quality deals command using ITAD's popularity-based filtering"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.itad_client = ITADClient()

    async def cog_unload(self):
        """Clean up when cog is unloaded"""
        if self.itad_client:
            await self.itad_client.close()

    async def _send_typing(self, ctx: commands.Context):
        """Send typing indicator"""
        try:
            await ctx.typing()
        except Exception:
            pass  # Ignore typing errors

    @commands.command(name="quality_deals", aliases=["quality", "q", "interesting"])
    async def quality_deals_command(
        self, 
        ctx: commands.Context, 
        store: Optional[str] = None,
        min_discount: int = 50,
        sort_by: str = "hottest"
    ) -> None:
        """
        Show quality game deals using ITAD's own approach for "interesting games"
        
        Uses ITAD's popularity data and quality filtering to show games similar to
        what you see on isthereanydeal.com/deals (interesting, not asset flips)
        
        Usage: !quality_deals [store] [min_discount] [sort]
        Example: !quality_deals steam 60 hottest
        
        Args:
            store: Store to filter by (Steam, Epic, GOG)
            min_discount: Minimum discount % (default: 50)
            sort_by: Sort method - hottest, newest, price, discount (default: hottest)
        """
        # Validate store parameter
        if store:
            store = store.lower().strip()
            allowed_stores = ['steam', 'epic', 'epic game store', 'gog', 'gog.com']
            if store not in allowed_stores:
                embed = create_error_embed(
                    "Invalid Store",
                    f"Quality deals only work with: {', '.join(['Steam', 'Epic Game Store', 'GOG'])}\\n"
                    f"You provided: `{store}`"
                )
                await ctx.send(embed=embed)
                return
        
        # Validate sort parameter
        valid_sorts = ['hottest', 'popular', 'newest', 'price', 'discount', 'cut']
        if sort_by.lower() not in valid_sorts:
            embed = create_error_embed(
                "Invalid Sort Method", 
                f"Valid options: {', '.join(valid_sorts)}\\n"
                f"You provided: `{sort_by}`"
            )
            await ctx.send(embed=embed)
            return
            
        await self._send_typing(ctx)
        
        try:
            # Use ITAD quality method
            deals = await self.itad_client.fetch_quality_deals_itad_method(
                limit=10,
                min_discount=min_discount,
                sort_by=sort_by.lower(),
                store_filter=store,
                use_popularity_stats=True
            )
            
            if not deals:
                embed = create_no_deals_embed(
                    "No Quality Deals Found",
                    f"No interesting games found with {min_discount}%+ discount"
                    f"{f' on {store.title()}' if store else ''}\\n"
                    "Try lowering the discount percentage or different store."
                )
                await ctx.send(embed=embed)
                return
            
            # Create embed with quality deals
            embed = create_deals_embed(
                deals=deals,
                title=f"🌟 Quality Game Deals ({sort_by.title()} Sort)",
                description=f"Showing {len(deals)} interesting games "
                           f"({min_discount}%+ discount{f', {store.title()} only' if store else ''})",
                footer_text="✨ Curated using ITAD's popularity data and quality filtering"
            )
            
            await ctx.send(embed=embed)
            
        except ValueError as e:
            embed = create_error_embed("API Error", str(e))
            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"Error in quality deals command: {e}")
            embed = create_error_embed(
                "Command Error", 
                "Failed to fetch quality deals. Please try again."
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(QualityDeals(bot))