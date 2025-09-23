# cogs/deals.py
import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import make_deal_embed

class Deals(commands.Cog):
    """Essential deal commands for GameDealer bot"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = getattr(bot, 'log', None)
        self.deals_channel_id = getattr(bot, 'deals_channel_id', 0)
    
    @app_commands.command(name="search_deals", description="Search for best deals from Steam, Epic, or GOG")
    @app_commands.describe(amount="Number of deals to show (1-25)")
    async def search_deals(self, interaction: discord.Interaction, amount: int = 10):
        """
        Search for best deals from Steam, Epic, or GOG (prioritized stores)
        Usage: /search_deals 15
        """
        if amount > 25:
            amount = 25
            try:
                await interaction.response.send_message("⚠️ Amount capped at 25 deals.", ephemeral=True)
                # Send a follow-up message for the actual search
                await interaction.followup.send(f"🔍 Searching for {amount} best deals from Steam, Epic & GOG...")
            except discord.NotFound:
                # Interaction expired, cannot respond
                if self.log:
                    self.log.warning("Interaction expired before response could be sent")
                return
        else:
            try:
                await interaction.response.send_message(f"🔍 Searching for {amount} best deals from Steam, Epic & GOG...")
            except discord.NotFound:
                # Interaction expired, cannot respond
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
                    if amount > 25:
                        await interaction.followup.send("❌ No deals found. Try again later or check API status.")
                    else:
                        await interaction.edit_original_response(content="❌ No deals found. Try again later or check API status.")
                except discord.NotFound:
                    # Interaction expired
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
                    if amount > 25:
                        await interaction.followup.send("❌ No quality deals found. Try again later or check API status.")
                    else:
                        await interaction.edit_original_response(content="❌ No quality deals found. Try again later or check API status.")
                except discord.NotFound:
                    # Interaction expired
                    if self.log:
                        self.log.warning("Could not send 'no quality deals found' message - interaction expired")
                return
            
            await self._display_deals(interaction, final_deals, f"Best Deals from Steam, Epic & GOG", amount > 25)
            
        except Exception as e:
            if self.log:
                self.log.error(f"Error searching deals: {e}")
            try:
                if amount > 25:
                    await interaction.followup.send(f"❌ Error searching deals: {str(e)}")
                else:
                    await interaction.edit_original_response(content=f"❌ Error searching deals: {str(e)}")
            except discord.NotFound:
                # Interaction expired
                if self.log:
                    self.log.warning("Could not send error message - interaction expired")

    @app_commands.command(name="search_store", description="Search for best deals from a specific store")
    @app_commands.describe(
        store="Store name (e.g., Steam, Epic, GOG)",
        amount="Number of deals to show (1-25)"
    )
    async def search_deals_by_store(self, interaction: discord.Interaction, store: str, amount: int = 10):
        """
        Search for best deals from a specific store
        Usage: /search_store Steam 15
        """
        if amount > 25:
            amount = 25
            try:
                await interaction.response.send_message("⚠️ Amount capped at 25 deals.", ephemeral=True)
                await interaction.followup.send(f"🔍 Searching for {amount} best deals from **{store}**...")
            except discord.NotFound:
                if self.log:
                    self.log.warning("Interaction expired before response could be sent (store search)")
                return
        else:
            try:
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
                if amount > 25:
                    await interaction.followup.send(f"❌ No deals found from **{store}**. Store might not have current promotions or check store name spelling.")
                else:
                    await interaction.edit_original_response(content=f"❌ No deals found from **{store}**. Store might not have current promotions or check store name spelling.")
                return
            
            await self._display_deals(interaction, final_deals, f"Best Deals from {store}", amount > 25)
            
        except Exception as e:
            if self.log:
                self.log.error(f"Error searching deals by store: {e}")
            if amount > 25:
                await interaction.followup.send(f"❌ Error searching deals from {store}: {str(e)}")
            else:
                await interaction.edit_original_response(content=f"❌ Error searching deals from {store}: {str(e)}")
    
    async def _display_deals(self, interaction: discord.Interaction, deals: list, title: str, is_followup: bool = False):
        """Display deals in a formatted embed with pagination for large lists"""
        if not deals:
            message = "No deals found."
            if is_followup:
                await interaction.followup.send(message)
            else:
                await interaction.edit_original_response(content=message)
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
        if is_followup:
            # Send first embed as followup
            await interaction.followup.send(content="✅ Search completed!", embed=embeds[0])
            # Send additional embeds as separate messages
            for embed in embeds[1:]:
                await interaction.followup.send(embed=embed)
        else:
            # Edit original response with first embed
            await interaction.edit_original_response(content="✅ Search completed!", embed=embeds[0])
            # Send additional embeds as followup messages
            for embed in embeds[1:]:
                await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="priority_search", description="Search ONLY for deals from your curated priority games database")
    @app_commands.describe(
        amount="Number of deals to show (1-25)",
        min_priority="Minimum priority level (1-10, default: 5)",
        min_discount="Minimum discount percentage (default: 1%)"
    )
    async def priority_search(self, interaction: discord.Interaction, amount: int = 10, min_priority: int = 5, min_discount: int = 1):
        """
        Search for deals ONLY from games in the priority database
        Usage: /priority_search 15 7 50 (15 deals, priority 7+, 50%+ discount)
        """
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
            
        try:
            await interaction.response.send_message(
                f"🎯 Searching for {amount} priority deals (min {min_priority}/10 priority, {min_discount}%+ discount)..."
            )
        except discord.NotFound:
            if self.log:
                self.log.warning("Interaction expired before response could be sent")
            return
        
        try:
            # Use STRICT priority filtering - only games from the database
            deals = await self.bot.itad_client.fetch_deals(
                min_discount=min_discount,
                limit=amount,
                quality_filter=True,  # Enable strict priority filtering
                min_priority=min_priority,
                log_full_response=True
            )
            
            if not deals:
                await interaction.edit_original_response(
                    content=f"❌ No priority deals found with your criteria:\n"
                           f"• Priority: {min_priority}/10 or higher\n"
                           f"• Discount: {min_discount}% or higher\n"
                           f"• Database: Only curated priority games\n\n"
                           f"💡 Try lowering the priority or discount requirements."
                )
                return
            
            # Add debug info to first few deals
            priority_info = []
            for i, deal in enumerate(deals[:3]):
                priority = deal.get('_priority', 'N/A')
                match_score = deal.get('_match_score', 'N/A')
                if isinstance(match_score, float):
                    match_score = f"{match_score:.2f}"
                priority_info.append(f"• {deal['title']}: Priority {priority}, Match {match_score}")
            
            debug_text = f"🎯 **Priority Search Results** ({len(deals)}/{amount} found)\n"
            debug_text += f"**Search criteria:** Priority {min_priority}+, Discount {min_discount}%+\n"
            debug_text += f"**Database:** {len(self.bot.itad_client.priority_filter.priority_games)} curated games\n\n"
            if priority_info:
                debug_text += "**Top matches:**\n" + "\n".join(priority_info[:3])
            
            # Create embeds with priority indicators
            embeds = []
            current_embed = make_deal_embed(title="🎯 Priority Game Deals", description=debug_text)
            current_embed.set_footer(text="⚡ Only curated priority games • Sorted by priority + discount")
            
            for i, deal in enumerate(deals):
                priority = deal.get('_priority', 0)
                priority_emoji = self._get_priority_emoji(priority)
                
                # Enhanced deal title with priority indicator
                enhanced_title = f"{priority_emoji} {deal['title']}"
                if priority:
                    enhanced_title += f" (P{priority})"
                
                value = f"~~{deal['original_price']}~~ **{deal['price']}** • {deal['discount']} off\n🏪 {deal['store']} • [View Deal]({deal['url']})"
                
                if len(current_embed.fields) < 10:
                    current_embed.add_field(name=enhanced_title, value=value, inline=False)
                else:
                    embeds.append(current_embed)
                    current_embed = make_deal_embed(title=f"🎯 Priority Game Deals (Page {len(embeds)+1})", description="")
                    current_embed.set_footer(text="⚡ Only curated priority games • Sorted by priority + discount")
                    current_embed.add_field(name=enhanced_title, value=value, inline=False)
            
            if current_embed.fields:
                embeds.append(current_embed)
            
            # Send the embeds
            await interaction.edit_original_response(content="✅ Priority search completed!", embed=embeds[0])
            for embed in embeds[1:]:
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            error_msg = f"❌ Error during priority search: {str(e)}"
            if self.log:
                self.log.error(f"Priority search error: {e}")
            
            try:
                await interaction.edit_original_response(content=error_msg)
            except discord.NotFound:
                if self.log:
                    self.log.warning("Could not send error message - interaction expired")
    
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