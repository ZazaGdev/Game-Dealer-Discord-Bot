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
            await interaction.response.send_message("⚠️ Amount capped at 25 deals.", ephemeral=True)
            # Send a follow-up message for the actual search
            await interaction.followup.send(f"🔍 Searching for {amount} best deals from Steam, Epic & GOG...")
        else:
            await interaction.response.send_message(f"🔍 Searching for {amount} best deals from Steam, Epic & GOG...")
        
        # Search across prioritized stores: Steam, Epic, GOG
        preferred_stores = ["Steam", "Epic Game Store", "GOG"]
        
        try:
            # First, try to get deals from preferred stores with a larger limit to account for filtering
            deals = await self.bot.itad_client.fetch_deals(
                min_discount=5,  # Lower threshold to get more options
                limit=amount * 5,  # Get more deals than needed to account for store filtering
                store_filter=None,  # We'll filter after fetching
                quality_filter=True,
                min_priority=4  # Include most games but filter out low quality
            )
            
            if not deals:
                if amount > 25:
                    await interaction.followup.send("❌ No deals found. Try again later or check API status.")
                else:
                    await interaction.edit_original_response(content="❌ No deals found. Try again later or check API status.")
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
                if amount > 25:
                    await interaction.followup.send("❌ No quality deals found. Try again later or check API status.")
                else:
                    await interaction.edit_original_response(content="❌ No quality deals found. Try again later or check API status.")
                return
                return
            
            await self._display_deals(interaction, final_deals, f"Best Deals from Steam, Epic & GOG", amount > 25)
            
        except Exception as e:
            if self.log:
                self.log.error(f"Error searching deals: {e}")
            if amount > 25:
                await interaction.followup.send(f"❌ Error searching deals: {str(e)}")
            else:
                await interaction.edit_original_response(content=f"❌ Error searching deals: {str(e)}")

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
            await interaction.response.send_message("⚠️ Amount capped at 25 deals.", ephemeral=True)
            await interaction.followup.send(f"🔍 Searching for {amount} best deals from **{store}**...")
        else:
            await interaction.response.send_message(f"🔍 Searching for {amount} best deals from **{store}**...")
        
        try:
            # For store-specific searches, get more deals than requested to account for quality filtering
            deals = await self.bot.itad_client.fetch_deals(
                min_discount=1,  # Very low threshold to get maximum options from the specific store
                limit=amount * 2,  # Get more deals than needed to account for quality filtering
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