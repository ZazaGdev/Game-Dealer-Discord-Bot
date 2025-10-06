# cogs/native_priority.py
"""
Native Priority Deals Discord Cog

Uses ITAD's native API endpoints for priority searching without local JSON database
"""

import logging
from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

from api.itad_client import ITADClient
from utils.embeds import create_deals_embed, create_error_embed, create_no_deals_embed


class NativePriority(commands.Cog):
    """Native ITAD priority search using popular games endpoints"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Use the bot's API key if available
        api_key = getattr(bot, 'itad_api_key', None)
        self.itad_client = ITADClient(api_key=api_key) if api_key else None

    async def cog_unload(self):
        """Clean up when cog is unloaded"""
        if self.itad_client:
            await self.itad_client.close()

    async def _send_typing(self, ctx: commands.Context):
        """Send typing indicator"""
        try:
            await ctx.typing()
        except Exception:
            pass

    @commands.hybrid_command(name="native_priority", aliases=["np", "native", "itad_priority"])
    @app_commands.describe(
        method="Priority calculation method",
        store="Store to filter by",
        min_discount="Minimum discount percentage (default: 30)"
    )
    @app_commands.choices(method=[
        app_commands.Choice(name="🔥 Hybrid (Recommended)", value="hybrid"),
        app_commands.Choice(name="📊 Popular Deals", value="popular_deals"),
        app_commands.Choice(name="💝 Waitlisted Deals", value="waitlisted_deals"),
        app_commands.Choice(name="🎮 Collected Deals", value="collected_deals")
    ])
    @app_commands.choices(store=[
        app_commands.Choice(name="Steam", value="steam"),
        app_commands.Choice(name="Epic Games Store", value="epic"),
        app_commands.Choice(name="GOG", value="gog"),
        app_commands.Choice(name="🎮 Xbox/Microsoft Store", value="xbox")
    ])
    async def native_priority_command(
        self,
        ctx: commands.Context,
        method: str = "hybrid",
        store: Optional[str] = None,
        min_discount: int = 30
    ) -> None:
        """
        Native ITAD priority search using their popularity endpoints
        
        Uses ITAD's own most-popular, most-waitlisted, and most-collected data
        to find the best deals for games people actually want and play.
        
        Methods:
        - hybrid: Combines all popularity sources (recommended)
        - popular_deals: Uses most-popular games endpoint
        - waitlisted_deals: Uses most-waitlisted games endpoint  
        - collected_deals: Uses most-collected games endpoint
        
        Usage: !native_priority [method] [store] [min_discount]
        Example: !native_priority hybrid steam 40
        
        Args:
            method: Priority calculation method (default: hybrid)
            store: Store to filter by (Steam, Epic, GOG, Xbox)
            min_discount: Minimum discount % (default: 30)
        """
        # Validate method parameter
        valid_methods = ['hybrid', 'popular_deals', 'waitlisted_deals', 'collected_deals']
        if method.lower() not in valid_methods:
            embed = create_error_embed(
                "Invalid Method",
                f"Valid methods: {', '.join(valid_methods)}\\n"
                f"You provided: `{method}`\\n\\n"
                "🔥 **hybrid** - Best overall results (recommended)\\n"
                "📊 **popular_deals** - Most popular games currently\\n" 
                "💝 **waitlisted_deals** - Most wanted games\\n"
                "🎮 **collected_deals** - Most owned games"
            )
            await ctx.send(embed=embed)
            return
        
        # Validate store parameter
        if store:
            store = store.lower().strip()
            allowed_stores = ['steam', 'epic', 'epic game store', 'gog', 'gog.com', 'microsoft store', 'xbox', 'microsoft']
            if store not in allowed_stores:
                embed = create_error_embed(
                    "Invalid Store",
                    f"Supported stores: {', '.join(['Steam', 'Epic Game Store', 'GOG', 'Xbox/Microsoft Store'])}\\n"
                    f"You provided: `{store}`"
                )
                await ctx.send(embed=embed)
                return
        
        # Validate discount parameter
        if min_discount < 0 or min_discount > 99:
            embed = create_error_embed(
                "Invalid Discount",
                f"Discount must be between 0 and 99\\n"
                f"You provided: `{min_discount}%`"
            )
            await ctx.send(embed=embed)
            return
        
        # Check if ITAD client is available
        if not self.itad_client:
            embed = create_error_embed(
                "API Key Missing",
                "ITAD API key is not configured. Please contact the bot administrator."
            )
            await ctx.send(embed=embed)
            return
        
        await self._send_typing(ctx)
        
        try:
            # Use native ITAD priority method
            deals = await self.itad_client.fetch_native_priority_deals(
                limit=10,
                min_discount=min_discount,
                store_filter=store,
                priority_method=method.lower()
            )
            
            if not deals:
                embed = create_no_deals_embed(
                    "No Priority Deals Found",
                    f"No popular games found with {min_discount}%+ discount using {method} method"
                    f"{f' on {store.title()}' if store else ''}\\n\\n"
                    "Try:\\n"
                    "• Lower the discount percentage\\n"
                    "• Different method (try `hybrid`)\\n"
                    "• Different store or remove store filter"
                )
                await ctx.send(embed=embed)
                return
            
            # Create embed with method-specific info
            method_descriptions = {
                "hybrid": "🔥 Combined popularity sources (most-popular + most-waitlisted + most-collected)",
                "popular_deals": "📊 Games from ITAD's most-popular endpoint",
                "waitlisted_deals": "💝 Games from ITAD's most-waitlisted endpoint", 
                "collected_deals": "🎮 Games from ITAD's most-collected endpoint"
            }
            
            method_icons = {
                "hybrid": "🔥",
                "popular_deals": "📊", 
                "waitlisted_deals": "💝",
                "collected_deals": "🎮"
            }
            
            icon = method_icons.get(method.lower(), "🎯")
            description = method_descriptions.get(method.lower(), f"Using {method} method")
            
            embed = create_deals_embed(
                deals=deals,
                title=f"{icon} Native ITAD Priority Deals ({method.title()})",
                description=f"{description}\\n"
                           f"Showing {len(deals)} deals ({min_discount}%+ discount"
                           f"{f', {store.title()} only' if store else ''})\\n",
                footer_text="🎯 Using ITAD's native popularity data • No local database required"
            )
            
            await ctx.send(embed=embed)
            
        except ValueError as e:
            embed = create_error_embed("API Error", str(e))
            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"Error in native priority command: {e}")
            embed = create_error_embed(
                "Command Error",
                "Failed to fetch native priority deals. Please try again."
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="priority_comparison", aliases=["pc", "compare_priority"])
    @app_commands.describe(
        store="Store to filter by",
        min_discount="Minimum discount percentage (default: 40)"
    )
    @app_commands.choices(store=[
        app_commands.Choice(name="Steam", value="steam"),
        app_commands.Choice(name="Epic Games Store", value="epic"),
        app_commands.Choice(name="GOG", value="gog"),
        app_commands.Choice(name="🎮 Xbox/Microsoft Store", value="xbox")
    ])
    async def priority_comparison_command(
        self,
        ctx: commands.Context,
        store: Optional[str] = None,
        min_discount: int = 40
    ) -> None:
        """
        Compare results from different ITAD priority methods
        
        Shows side-by-side comparison of:
        - Hybrid method (recommended)
        - Most popular games
        - Most waitlisted games
        - Most collected games
        
        Usage: !priority_comparison [store] [min_discount]
        Example: !priority_comparison steam 50
        """
        # Validate store parameter
        if store:
            store = store.lower().strip()
            allowed_stores = ['steam', 'epic', 'epic game store', 'gog', 'gog.com', 'microsoft store', 'xbox', 'microsoft']
            if store not in allowed_stores:
                embed = create_error_embed(
                    "Invalid Store",
                    f"Supported stores: {', '.join(['Steam', 'Epic Game Store', 'GOG', 'Xbox/Microsoft Store'])}\\n"
                    f"You provided: `{store}`"
                )
                await ctx.send(embed=embed)
                return
        
        # Check if ITAD client is available
        if not self.itad_client:
            embed = create_error_embed(
                "API Key Missing", 
                "ITAD API key is not configured. Please contact the bot administrator."
            )
            await ctx.send(embed=embed)
            return
        
        await self._send_typing(ctx)
        
        try:
            # Get results from all methods
            methods = [
                ("hybrid", "🔥 Hybrid (Recommended)"),
                ("popular_deals", "📊 Most Popular"),
                ("waitlisted_deals", "💝 Most Waitlisted"), 
                ("collected_deals", "🎮 Most Collected")
            ]
            
            all_results = {}
            
            for method_id, method_name in methods:
                try:
                    deals = await self.itad_client.fetch_native_priority_deals(
                        limit=5,  # Smaller limit for comparison
                        min_discount=min_discount,
                        store_filter=store,
                        priority_method=method_id
                    )
                    all_results[method_id] = (method_name, deals)
                except Exception as e:
                    logging.warning(f"Failed to get {method_id} results: {e}")
                    all_results[method_id] = (method_name, [])
            
            # Create comparison embed
            embed = discord.Embed(
                title="🎯 ITAD Priority Methods Comparison",
                description=f"Comparing different native ITAD priority approaches\\n"
                           f"Filters: {min_discount}%+ discount{f', {store.title()} only' if store else ''}",
                color=0x00FF00,
                timestamp=discord.utils.utcnow()
            )
            
            for method_id, (method_name, deals) in all_results.items():
                if deals:
                    game_list = []
                    for i, deal in enumerate(deals[:3], 1):  # Show top 3 per method
                        game_list.append(f"{i}. **{deal['title']}** - {deal['price']} ({deal.get('discount', 'N/A')})")
                    
                    field_value = "\\n".join(game_list)
                    if len(deals) > 3:
                        field_value += f"\\n*...and {len(deals) - 3} more*"
                else:
                    field_value = "*No deals found*"
                
                embed.add_field(
                    name=f"{method_name} ({len(deals)} deals)",
                    value=field_value,
                    inline=False
                )
            
            embed.set_footer(text="💡 Use !native_priority hybrid for best overall results")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"Error in priority comparison: {e}")
            embed = create_error_embed(
                "Comparison Error",
                "Failed to compare priority methods. Please try again."
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(NativePriority(bot))