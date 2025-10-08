# cogs/deals.py
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Union, List, Any, TYPE_CHECKING
import logging
from utils.embeds import make_deal_embed
from models import Deal, InteractionOrContext, StoreFilter

if TYPE_CHECKING:
    from api.itad_client import ITADClient

class Deals(commands.Cog):
    """Essential deal commands for GameDealer bot"""
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.log: Optional[logging.Logger] = getattr(bot, 'log', None)
        self.deals_channel_id: int = getattr(bot, 'deals_channel_id', 0)
    
    # Traditional prefix command
    @commands.command(name="search_deals", help="Search for best deals from Steam, Epic, or GOG")
    async def search_deals_prefix(self, ctx: commands.Context, amount: int = 10):
        """
        Traditional prefix command for searching deals
        Usage: !search_deals 15
        """
        # Convert to interaction-like behavior for code reuse
        class MockInteraction:
            def __init__(self, ctx: commands.Context) -> None:
                self.ctx: commands.Context = ctx
                self._response_sent: bool = False
            
            async def response_send_message(self, content: str, ephemeral: bool = False) -> None:
                await self.ctx.send(content)
                self._response_sent = True
            
            async def edit_original_response(self, content: Optional[str] = None, embed: Optional[discord.Embed] = None) -> None:
                if embed:
                    await self.ctx.send(content=content, embed=embed)
                else:
                    await self.ctx.send(content)
            
            async def followup_send(self, content: Optional[str] = None, embed: Optional[discord.Embed] = None) -> None:
                if embed:
                    await self.ctx.send(content=content, embed=embed)
                else:
                    await self.ctx.send(content)
            
            @property
            def response(self) -> 'MockInteraction':
                return self
            
            @property
            def followup(self) -> 'MockInteraction':
                return self
        
        mock_interaction = MockInteraction(ctx)
        await self._search_deals_logic(mock_interaction, amount, is_prefix=True)

    # Slash command
    @app_commands.command(name="search_deals", description="Search for best deals from Steam, Epic, or GOG")
    @app_commands.describe(amount="Number of deals to show (1-25)")
    async def search_deals(self, interaction: discord.Interaction, amount: int = 10):
        """
        Slash command for searching deals  
        Usage: /search_deals 15
        """
        await self._search_deals_logic(interaction, amount, is_prefix=False)

    async def _search_deals_logic(self, interaction_or_ctx: InteractionOrContext, amount: int, is_prefix: bool = False) -> None:
        """
        Shared logic for both slash and prefix commands
        """
        # Normalize the interaction/context interface
        if is_prefix:
            # For prefix commands, interaction_or_ctx is the mock interaction
            interaction = interaction_or_ctx
        else:
            # For slash commands, it's a real interaction
            interaction = interaction_or_ctx
            
        if amount > 25:
            amount = 25
            try:
                if is_prefix:
                    await interaction.ctx.send("⚠️ Amount capped at 25 deals.")
                    await interaction.ctx.send(f"🔍 Searching for {amount} best deals from Steam, Epic & GOG...")
                else:
                    await interaction.response.send_message("⚠️ Amount capped at 25 deals.", ephemeral=True)
                    await interaction.followup.send(f"🔍 Searching for {amount} best deals from Steam, Epic & GOG...")
            except discord.NotFound:
                if self.log:
                    self.log.warning("Interaction expired before response could be sent")
                return
        else:
            try:
                if is_prefix:
                    await interaction.ctx.send(f"🔍 Searching for {amount} best deals from Steam, Epic & GOG...")
                else:
                    await interaction.response.send_message(f"🔍 Searching for {amount} best deals from Steam, Epic & GOG...")
            except discord.NotFound:
                if self.log:
                    self.log.warning("Interaction expired before response could be sent")
                return
        
        # Search across prioritized stores: Steam, Epic, GOG
        preferred_stores = ["Steam", "Epic Game Store", "GOG"]
        
        try:
            # First, try to get deals from preferred stores with a larger limit to account for strict filtering
            deals = await self.bot.itad_client.fetch_deals(
                min_discount=5,  # Lower threshold to get more options
                limit=amount * 10,  # Get significantly more deals since we're filtering strictly to priority games only
                store_filter=None,  # We'll filter after fetching
                quality_filter=True,
                min_priority=4  # Include most games but filter out low quality
            )
            
            if not deals:
                try:
                    if is_prefix:
                        await interaction.ctx.send("❌ No deals found. Try again later or check API status.")
                    elif amount > 25:
                        await interaction.followup.send("❌ No deals found. Try again later or check API status.")
                    else:
                        await interaction.edit_original_response(content="❌ No deals found. Try again later or check API status.")
                except discord.NotFound:
                    if self.log:
                        self.log.warning("Could not send 'no deals found' message - interaction expired")
                return
            
            # Filter for preferred stores first
            preferred_deals = []
            other_deals = []
            
            for deal in deals:
                store_name = deal.get('store', '')
                if any(preferred_store.lower() in store_name.lower() for preferred_store in preferred_stores):
                    preferred_deals.append(deal)
                else:
                    other_deals.append(deal)
            
            # Use preferred deals first, then fill with other quality deals if needed
            final_deals = preferred_deals[:amount]
            
            # If we don't have enough from preferred stores, add other quality deals
            if len(final_deals) < amount:
                remaining_needed = amount - len(final_deals)
                final_deals.extend(other_deals[:remaining_needed])
            
            if not final_deals:
                try:
                    if is_prefix:
                        await interaction.ctx.send("❌ No quality deals found. Try again later or check API status.")
                    elif amount > 25:
                        await interaction.followup.send("❌ No quality deals found. Try again later or check API status.")
                    else:
                        await interaction.edit_original_response(content="❌ No quality deals found. Try again later or check API status.")
                except discord.NotFound:
                    if self.log:
                        self.log.warning("Could not send 'no quality deals found' message - interaction expired")
                return
            
            await self._display_deals(interaction, final_deals, f"Best Deals from Steam, Epic & GOG", amount > 25, is_prefix)
            
        except Exception as e:
            if self.log:
                self.log.error(f"Error searching deals: {e}")
            try:
                if is_prefix:
                    await interaction.ctx.send(f"❌ Error searching deals: {str(e)}")
                elif amount > 25:
                    await interaction.followup.send(f"❌ Error searching deals: {str(e)}")
                else:
                    await interaction.edit_original_response(content=f"❌ Error searching deals: {str(e)}")
            except discord.NotFound:
                if self.log:
                    self.log.warning("Could not send error message - interaction expired")

    # Traditional prefix command
    @commands.command(name="search_store", help="Search for best deals from a specific store")
    async def search_store_prefix(self, ctx: commands.Context, store: str, amount: int = 10):
        """
        Traditional prefix command for searching deals by store
        Usage: !search_store Steam 15
        """
        # Convert to interaction-like behavior for code reuse
        class MockInteraction:
            def __init__(self, ctx):
                self.ctx = ctx
        
        mock_interaction = MockInteraction(ctx)
        await self._search_store_logic(mock_interaction, store, amount, is_prefix=True)

    # Slash command

    @app_commands.command(name="search_store", description="Search for best deals from a specific store")
    @app_commands.describe(
        store="Store name (e.g., Steam, Epic, GOG)",
        amount="Number of deals to show (1-25)"
    )
    async def search_deals_by_store(self, interaction: discord.Interaction, store: str, amount: int = 10):
        """
        Slash command for searching deals by store
        Usage: /search_store Steam 15
        """
        await self._search_store_logic(interaction, store, amount, is_prefix=False)

    async def _search_store_logic(self, interaction_or_ctx, store: str, amount: int, is_prefix: bool = False):
        """
        Shared logic for both slash and prefix store search commands
        """
        # Normalize the interaction/context interface
        if is_prefix:
            interaction = interaction_or_ctx
        else:
            interaction = interaction_or_ctx
            
        if amount > 25:
            amount = 25
            try:
                if is_prefix:
                    await interaction.ctx.send("⚠️ Amount capped at 25 deals.")
                    await interaction.ctx.send(f"🔍 Searching for {amount} best deals from **{store}**...")
                else:
                    await interaction.response.send_message("⚠️ Amount capped at 25 deals.", ephemeral=True)
                    await interaction.followup.send(f"🔍 Searching for {amount} best deals from **{store}**...")
            except discord.NotFound:
                if self.log:
                    self.log.warning("Interaction expired before response could be sent (store search)")
                return
        else:
            try:
                if is_prefix:
                    await interaction.ctx.send(f"🔍 Searching for {amount} best deals from **{store}**...")
                else:
                    await interaction.response.send_message(f"🔍 Searching for {amount} best deals from **{store}**...")
            except discord.NotFound:
                if self.log:
                    self.log.warning("Interaction expired before response could be sent (store search)")
                return
        
        try:
            # For store-specific searches, get more deals than requested to account for strict priority filtering
            deals = await self.bot.itad_client.fetch_deals(
                min_discount=1,  # Very low threshold to get maximum options from the specific store
                limit=amount * 15,  # Get many more deals since we're now strictly filtering to priority games only
                store_filter=store,
                quality_filter=True,
                min_priority=4
            )
            
            # Take only the amount requested
            final_deals = deals[:amount]
            
            if not final_deals:
                message = f"❌ No deals found from **{store}**. Store might not have current promotions or check store name spelling."
                if is_prefix:
                    await interaction.ctx.send(message)
                elif amount > 25:
                    await interaction.followup.send(message)
                else:
                    await interaction.edit_original_response(content=message)
                return
            
            await self._display_deals(interaction, final_deals, f"Best Deals from {store}", amount > 25, is_prefix)
            
        except Exception as e:
            if self.log:
                self.log.error(f"Error searching deals by store: {e}")
            error_message = f"❌ Error searching deals from {store}: {str(e)}"
            if is_prefix:
                await interaction.ctx.send(error_message)
            elif amount > 25:
                await interaction.followup.send(error_message)
            else:
                await interaction.edit_original_response(content=error_message)
    
    async def _display_deals(self, interaction_or_ctx, deals: list, title: str, is_followup: bool = False, is_prefix: bool = False):
        """Display deals in a formatted embed with pagination for large lists"""
        if not deals:
            message = "No deals found."
            if is_prefix:
                await interaction_or_ctx.ctx.send(message)
            elif is_followup:
                await interaction_or_ctx.followup.send(message)
            else:
                await interaction_or_ctx.edit_original_response(content=message)
            return
        
        # Discord embed limits: 25 fields max, so we'll use 10 deals per embed for readability
        deals_per_embed = 10
        total_pages = (len(deals) + deals_per_embed - 1) // deals_per_embed
        
        # Create embeds for all pages
        embeds = []
        for page in range(total_pages):
            start_idx = page * deals_per_embed
            end_idx = min(start_idx + deals_per_embed, len(deals))
            page_deals = deals[start_idx:end_idx]
            
            # Create embed for this page
            page_title = f"🎮 {title}"
            if total_pages > 1:
                page_title += f" (Page {page + 1}/{total_pages})"
                
            embed = discord.Embed(
                title=page_title,
                description=f"Found {len(deals)} great deals • Sorted by discount % • Showing {start_idx + 1}-{end_idx}",
                color=0x00ff00
            )
            
            for i, deal in enumerate(page_deals):
                global_index = start_idx + i + 1
                
                # Get priority emoji if available
                priority_emoji = ""
                if deal.get('_priority'):
                    priority_emoji = self._get_priority_emoji(deal['_priority'])
                
                # Format price information
                price_info = f"**{deal['price']}**"
                if deal.get('original_price'):
                    price_info += f" ~~{deal['original_price']}~~"
                
                # Create deal description
                discount_text = f" **{deal.get('discount', 'N/A')}**" if deal.get('discount') else ""
                value = f"{price_info} at {deal['store']}{discount_text} {priority_emoji}"
                
                if deal.get('url'):
                    value += f"\n[🔗 Get Deal]({deal['url']})"
                
                # Truncate title if too long
                title_text = deal['title']
                if len(title_text) > 45:
                    title_text = title_text[:42] + "..."
                
                embed.add_field(
                    name=f"{global_index}. {title_text}",
                    value=value,
                    inline=False
                )
            
            # Set footer
            if page == 0:
                embed.set_footer(text="🎯 Deals sorted by highest discount percentage")
            else:
                embed.set_footer(text=f"🎯 Page {page + 1} of {total_pages} • Deals sorted by highest discount percentage")
            
            embeds.append(embed)
        
        # Send the embeds
        if is_prefix:
            # For prefix commands, send directly to channel
            await interaction_or_ctx.ctx.send(content="✅ Search completed!", embed=embeds[0])
            # Send additional embeds as separate messages
            for embed in embeds[1:]:
                await interaction_or_ctx.ctx.send(embed=embed)
        elif is_followup:
            # Send first embed as followup
            await interaction_or_ctx.followup.send(content="✅ Search completed!", embed=embeds[0])
            # Send additional embeds as separate messages
            for embed in embeds[1:]:
                await interaction_or_ctx.followup.send(embed=embed)
        else:
            # Edit original response with first embed
            await interaction_or_ctx.edit_original_response(content="✅ Search completed!", embed=embeds[0])
            # Send additional embeds as followup messages
            for embed in embeds[1:]:
                await interaction_or_ctx.followup.send(embed=embed)

    # Traditional prefix command
    @commands.command(name="priority_search", help="Search ONLY for deals from curated priority games database")
    async def priority_search_prefix(self, ctx: commands.Context, amount: int = 10, min_priority: int = 1, min_discount: int = 1, store: str = None):
        """
        Traditional prefix command for priority search
        Usage: !priority_search 15 3 25 Steam (15 deals, priority 3+, 25%+ discount, Steam only)
        """
        # Convert to interaction-like behavior for code reuse
        class MockInteraction:
            def __init__(self, ctx):
                self.ctx = ctx
        
        mock_interaction = MockInteraction(ctx)
        await self._priority_search_logic(mock_interaction, amount, min_priority, min_discount, store, is_prefix=True)

    # Slash command
    
    @app_commands.command(name="priority_search", description="Search ONLY for deals from your curated priority games database")
    @app_commands.describe(
        amount="Number of deals to show (1-25)",
        min_priority="Minimum priority level (1-10, default: 1)",
        min_discount="Minimum discount percentage (default: 1%)",
        store="Store name (e.g., Steam, Epic, GOG - optional)"
    )
    async def priority_search(self, interaction: discord.Interaction, amount: int = 10, min_priority: int = 1, min_discount: int = 1, store: str = None):
        """
        Slash command for priority search
        Usage: /priority_search amount:15 min_priority:3 min_discount:25 store:Steam
        """
        await self._priority_search_logic(interaction, amount, min_priority, min_discount, store, is_prefix=False)

    async def _priority_search_logic(self, interaction_or_ctx, amount: int, min_priority: int, min_discount: int, store: str = None, is_prefix: bool = False):
        """
        PROPER priority search implementation:
        1. Fetch large number of discounted games from ITAD (Steam, Epic, GOG by default or specific store)
        2. Load priority_games.json database
        3. Match discounted games against priority database
        4. Filter by priority level and discount requirements
        5. Return only matched games or friendly error if no matches
        """
        # Validate store - Priority search only works with Steam, Epic, and GOG
        allowed_stores = ['steam', 'epic', 'epic game store', 'gog', 'gog.com', 'microsoft store', 'xbox', 'microsoft']
        if store and store.lower() not in allowed_stores:
            error_msg = (
                f"❌ Priority search only supports Steam, Epic Game Store, and GOG.\n"
                f"You requested: {store}\n"
                f"Please use one of: Steam, Epic, GOG"
            )
            if is_prefix:
                await interaction_or_ctx.ctx.send(error_msg)
            else:
                await interaction_or_ctx.edit_original_response(content=error_msg)
            return
            
        # Normalize input parameters
        if amount > 25:
            amount = 25
        if min_priority > 10:
            min_priority = 10
        if min_priority < 1:
            min_priority = 1
        if min_discount > 100:
            min_discount = 100
        if min_discount < 1:
            min_discount = 1
            
        # Create search message
        store_text = f" from {store}" if store else " from Steam, Epic & GOG"
        search_message = f"🎯 Searching for priority deals{store_text} (min P{min_priority}, {min_discount}%+ discount)..."
        
        try:
            if is_prefix:
                await interaction_or_ctx.ctx.send(search_message)
            else:
                await interaction_or_ctx.response.send_message(search_message)
        except discord.NotFound:
            if self.log:
                self.log.warning("Interaction expired before response could be sent")
            return
        
        try:
            # Step 1: Load priority games database
            import json
            import os
            
            priority_db_path = "data/priority_games.json"
            if not os.path.exists(priority_db_path):
                error_msg = "❌ Priority games database not found!"
                if is_prefix:
                    await interaction_or_ctx.ctx.send(error_msg)
                else:
                    await interaction_or_ctx.edit_original_response(content=error_msg)
                return
            
            with open(priority_db_path, 'r', encoding='utf-8-sig') as f:
                priority_data = json.load(f)
            
            priority_games = priority_data.get('games', [])
            if not priority_games:
                error_msg = "❌ No games found in priority database!"
                if is_prefix:
                    await interaction_or_ctx.ctx.send(error_msg)
                else:
                    await interaction_or_ctx.edit_original_response(content=error_msg)
                return
            
            # Step 2: Use ITAD client's built-in priority filtering (much more effective!)
            try:
                priority_deals = await self.bot.itad_client.fetch_deals(
                    limit=amount * 3,  # Get more than requested to account for sorting/filtering
                    min_discount=min_discount,
                    store_filter=store,
                    quality_filter=True,  # Use ITAD client's priority filtering
                    min_priority=min_priority,
                    log_full_response=False
                )
                
                if not priority_deals:
                    no_deals_msg = (
                        f"❌ No priority games found matching your criteria:\n"
                        f"• Priority: {min_priority}/10 or higher\n"
                        f"• Discount: {min_discount}% or higher\n"
                        f"• Store: {store if store else 'Steam, Epic, GOG'}\n"
                        f"💡 Try lowering the priority or discount requirements, or check different stores."
                    )
                    if is_prefix:
                        await interaction_or_ctx.ctx.send(no_deals_msg)
                    else:
                        await interaction_or_ctx.edit_original_response(content=no_deals_msg)
                    return
                
                # Limit to requested amount
                final_deals = priority_deals[:amount]
                
                # Step 3: Create and send results
                await self._display_priority_results(interaction_or_ctx, final_deals, min_priority, min_discount, store, amount, len(priority_deals), len(priority_games), is_prefix)
                return
                
            except Exception as e:
                if self.log:
                    self.log.error(f"ITAD client priority search failed: {e}")
                # Fall back to manual matching if ITAD client fails
                pass
            
            # Fallback manual matching (only if ITAD client failed)
            # This code should not normally be reached since we use ITAD client priority filtering above
            error_msg = f"❌ Priority search temporarily unavailable. Please try again later."
            if is_prefix:
                await interaction_or_ctx.ctx.send(error_msg)
            else:
                await interaction_or_ctx.edit_original_response(content=error_msg)
            return
                
        except Exception as e:
            error_msg = f"❌ Error during priority search: {str(e)}"
            if self.log:
                self.log.error(f"Priority search error: {e}")
            
            try:
                if is_prefix:
                    await interaction_or_ctx.ctx.send(error_msg)
                else:
                    await interaction_or_ctx.edit_original_response(content=error_msg)
            except discord.NotFound:
                if self.log:
                    self.log.warning("Could not send error message - interaction expired")

    async def _display_priority_results(self, interaction_or_ctx, deals: list, min_priority: int, min_discount: int, store: str, requested_amount: int, total_matches: int, total_priority_games: int, is_prefix: bool):
        """Display priority search results with detailed information"""
        
        # Create summary information
        store_text = store if store else "Steam, Epic & GOG"
        summary = (
            f"🎯 **Priority Search Results** ({len(deals)}/{requested_amount} requested, {total_matches} total matches)\n"
            f"**Criteria:** Priority {min_priority}+, Discount {min_discount}%+, Store: {store_text}\n"
        )
        
        # Add top matches info
        if deals:
            top_matches = []
            for i, deal in enumerate(deals[:3]):
                priority = deal.get('_priority', 'N/A')
                discount = deal.get('discount', 'N/A')
                title = deal.get('_priority_title', deal.get('title', 'Unknown'))
                top_matches.append(f"• {title}: P{priority}, {discount} off")
            summary += "**Top matches:**\n" + "\n".join(top_matches)
        
        # Create embeds
        embeds = []
        current_embed = discord.Embed(
            title="🎯 Priority Game Deals", 
            description=summary,
            color=0x00ff00
        )
        current_embed.set_footer(text="⚡ Only curated priority games • Matched from database")
        
        for i, deal in enumerate(deals):
            priority = deal.get('_priority', 0)
            priority_emoji = self._get_priority_emoji(priority)
            category = deal.get('_category', '')
            
            # Enhanced deal title with priority and category
            enhanced_title = f"{priority_emoji} {deal.get('_priority_title', deal.get('title', 'Unknown'))}"
            if category:
                enhanced_title += f" ({category})"
            enhanced_title += f" [P{priority}]"
            
            # Enhanced value with notes
            value = f"~~{deal.get('original_price', 'N/A')}~~ **{deal.get('price', 'N/A')}** • {deal.get('discount', 'N/A')} off\n"
            value += f"🏪 {deal.get('store', 'Unknown Store')}"
            
            if deal.get('url'):
                value += f" • [View Deal]({deal.get('url')})"
            
            if deal.get('_notes'):
                value += f"\n💡 {deal.get('_notes')}"
            
            if len(current_embed.fields) < 10:
                current_embed.add_field(name=enhanced_title, value=value, inline=False)
            else:
                embeds.append(current_embed)
                current_embed = discord.Embed(
                    title=f"🎯 Priority Game Deals (Page {len(embeds)+1})", 
                    description="",
                    color=0x00ff00
                )
                current_embed.set_footer(text="⚡ Only curated priority games • Matched from database")
                current_embed.add_field(name=enhanced_title, value=value, inline=False)
        
        if current_embed.fields:
            embeds.append(current_embed)
        
        # Send the embeds
        if is_prefix:
            await interaction_or_ctx.ctx.send(content="✅ Priority search completed!", embed=embeds[0])
            for embed in embeds[1:]:
                await interaction_or_ctx.ctx.send(embed=embed)
        else:
            await interaction_or_ctx.edit_original_response(content="✅ Priority search completed!", embed=embeds[0])
            for embed in embeds[1:]:
                await interaction_or_ctx.followup.send(embed=embed)

    def _get_priority_emoji(self, priority: int) -> str:
        """Get emoji representation for priority level"""
        if priority >= 9:
            return "🏆"  # Trophy for top-tier games
        elif priority >= 7:
            return "⭐"  # Star for great games
        elif priority >= 5:
            return "✨"  # Sparkles for good games
        elif priority >= 3:
            return "🔹"  # Small diamond for decent games
        else:
            return "⚪"  # Circle for lower priority


async def setup(bot: commands.Bot):
    await bot.add_cog(Deals(bot))