# cogs/deals.py
import discord
from discord.ext import commands
from utils.embeds import make_deal_embed

class Deals(commands.Cog):
    """Advanced deal commands using ITAD API"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = getattr(bot, 'log', None)
        self.deals_channel_id = getattr(bot, 'deals_channel_id', 0)
    
    @commands.command(aliases=['search', 'find'])
    async def search_deals(self, ctx: commands.Context, min_discount: int = 30, limit: int = 10, *, store: str = None):
        """
        Search for deals with custom filters (with quality filtering enabled by default)
        Usage: !search_deals 70 15
        Usage: !search_deals 50 10 Steam
        Usage: !search_deals 60 5 Epic Game Store
        """
        await self._search_deals_internal(ctx, min_discount, limit, store, quality_filter=True)
    
    @commands.command(aliases=['all_search', 'raw_search'])
    async def search_all_deals(self, ctx: commands.Context, min_discount: int = 30, limit: int = 10, *, store: str = None):
        """
        Search for ALL deals including courses and tutorials (no quality filtering)
        Usage: !search_all_deals 70 15
        Usage: !search_all_deals 50 10 Steam
        """
        await self._search_deals_internal(ctx, min_discount, limit, store, quality_filter=False)
    
    @commands.command(aliases=['quality', 'games'])
    async def quality_deals(self, ctx: commands.Context, min_discount: int = 30, limit: int = 10, *, store: str = None):
        """
        Search for quality game deals only (explicitly filtered)
        Usage: !quality_deals 60 10
        Usage: !quality_deals 50 15 Steam
        """
        await self._search_deals_internal(ctx, min_discount, limit, store, quality_filter=True)
    
    async def _search_deals_internal(self, ctx: commands.Context, min_discount: int = 30, limit: int = 10, 
                                   store: str = None, quality_filter: bool = True):
        """Internal method to handle deal searching with quality filtering option"""
        if not self.bot.itad_client:
            await ctx.send("❌ ITAD API not configured. Please check your API key.")
            return
        
        if limit > 25:
            limit = 25
            await ctx.send("⚠️ Limit capped at 25 deals.")
        
        # Build search message
        filter_type = "quality games" if quality_filter else "all deals"
        search_text = f"🔍 Searching for {limit} {filter_type} with minimum {min_discount}% discount"
        if store:
            search_text += f" from **{store}**"
        search_text += "..."
        
        search_msg = await ctx.send(search_text)
        
        try:
            deals = await self.bot.itad_client.fetch_deals(
                min_discount=min_discount,
                limit=limit,
                store_filter=store,
                log_full_response=True,  # Always log full response for Discord commands
                quality_filter=quality_filter
            )
            
            if not deals:
                filter_text = "quality games" if quality_filter else "deals"
                error_msg = f"❌ No {filter_text} found with {min_discount}% minimum discount"
                if store:
                    error_msg += f" from **{store}**"
                    if quality_filter:
                        error_msg += f"\n💡 Try:\n• Lower discount threshold (e.g., `!search_deals 10 10 {store}`)\n• Different store (`!list_stores` to see available)\n• Include all deals (`!search_all_deals {min_discount} {limit} {store}`)\n• Remove store filter (`!search_deals {min_discount} {limit}`)"
                    else:
                        error_msg += f"\n💡 Try:\n• Lower discount threshold (e.g., `!search_all_deals 10 10 {store}`)\n• Different store (`!list_stores` to see available)\n• Remove store filter (`!search_all_deals {min_discount} {limit}`)"
                else:
                    if quality_filter:
                        error_msg += f"\n💡 Try:\n• Lower discount threshold (e.g., `!search_deals 10 {limit}`)\n• Include all deals (`!search_all_deals {min_discount} {limit}`)"
                    else:
                        error_msg += f"\n💡 Try lowering the discount threshold (e.g., `!search_all_deals 10 {limit}`)"
                await search_msg.edit(content=error_msg)
                return
            
            # Create embeds for all deals, splitting if necessary due to Discord limits
            embeds_data = []
            deals_per_embed = 10  # Discord embed field limit is 25, but we want readability
            
            for page in range(0, len(deals), deals_per_embed):
                page_deals = deals[page:page + deals_per_embed]
                page_num = (page // deals_per_embed) + 1
                total_pages = (len(deals) + deals_per_embed - 1) // deals_per_embed
                
                embed = discord.Embed(
                    title=f"🎮 Found {len(deals)} Great {'Games' if quality_filter else 'Deals'}!" + (f" (Page {page_num}/{total_pages})" if total_pages > 1 else ""),
                    description=f"{'Quality games only • ' if quality_filter else 'All deals • '}Minimum discount: {min_discount}%" + (f" • Store: **{store}**" if store else ""),
                    color=0x00ff00 if quality_filter else 0xffaa00,
                    timestamp=ctx.message.created_at
                )
                
                # Add deals as fields for this page
                for i, deal in enumerate(page_deals):
                    global_index = page + i + 1
                    discount_text = f" ({deal.get('discount', 'N/A')})" if deal.get('discount') else ""
                    
                    # Create a more compact value to fit more information
                    price_info = f"**{deal['price']}**"
                    if deal.get('original_price'):
                        price_info += f" ~~{deal['original_price']}~~"
                    
                    value = f"{price_info} at {deal['store']}{discount_text}"
                    
                    if deal.get('url'):
                        value += f"\n[🔗 Get Deal]({deal['url']})"
                    
                    # Truncate title if too long
                    title = deal['title']
                    if len(title) > 45:
                        title = title[:42] + "..."
                    
                    embed.add_field(
                        name=f"{global_index}. {title}",
                        value=value,
                        inline=False
                    )
                
                if page_num == 1:
                    footer_text = "Use !post_best to share the top deal"
                    if quality_filter:
                        footer_text += " • !search_all_deals for all results"
                    else:
                        footer_text += " • !quality_deals for games only"
                    if total_pages > 1:
                        footer_text += f" • {total_pages} pages total"
                    embed.set_footer(text=footer_text)
                else:
                    embed.set_footer(text=f"Page {page_num} of {total_pages}")
                
                embeds_data.append(embed)
            
            # Send the first embed by editing the search message
            await search_msg.edit(content="✅ Search completed!", embed=embeds_data[0])
            
            # Send additional embeds as separate messages if needed
            if len(embeds_data) > 1:
                for embed in embeds_data[1:]:
                    await ctx.send(embed=embed)
            
            # Store deals for other commands to use
            self.bot._last_deals = deals
            
        except ValueError as e:
            await search_msg.edit(content=f"❌ Configuration error: {str(e)}")
        except Exception as e:
            if self.log:
                self.log.error(f"Error searching deals: {e}")
                import traceback
                self.log.error(f"Full traceback: {traceback.format_exc()}")
            # Show actual error for debugging
            await search_msg.edit(content=f"❌ Error: {type(e).__name__}: {str(e)}")
            # Also send traceback in a code block for debugging
            import traceback
            tb = traceback.format_exc()
            if len(tb) > 1900:  # Discord message limit
                tb = tb[-1900:]  # Show last 1900 chars
            await ctx.send(f"```\n{tb}\n```")
    
    @commands.command()
    async def post_best(self, ctx: commands.Context):
        """Post the best deal from last search to deals channel"""
        if not hasattr(self.bot, '_last_deals') or not self.bot._last_deals:
            await ctx.send("❌ No deals found. Use `!search_deals` first.")
            return
        
        best_deal = self.bot._last_deals[0]
        
        # Convert Deal to dict format for existing function
        deal_dict = {
            "title": best_deal["title"],
            "price": best_deal["price"],
            "store": best_deal["store"],
            "url": best_deal.get("url", ""),
            "discount": best_deal.get("discount"),
            "original_price": best_deal.get("original_price")
        }
        
        # Get the general cog to use its send function
        general_cog = self.bot.get_cog("General")
        if general_cog:
            success = await general_cog.send_deal_to_discord(deal_dict)
            if success:
                await ctx.send(f"✅ Posted best deal: **{best_deal['title']}** to deals channel!")
            else:
                await ctx.send("❌ Failed to post deal to channel.")
        else:
            await ctx.send("❌ Could not access deals posting functionality.")
    
    @commands.command(aliases=['top', 'best'])
    async def top_deals(self, ctx: commands.Context, count: int = 5, *, store: str = None):
        """Get top quality game deals quickly with optional store filter"""
        await self._search_deals_internal(ctx, min_discount=30, limit=count, store=store, quality_filter=True)
    
    @commands.command(aliases=['stores'])
    async def list_stores(self, ctx: commands.Context):
        """List available stores for filtering"""
        if not self.bot.itad_client:
            await ctx.send("❌ ITAD API not configured.")
            return
        
        stores = self.bot.itad_client.get_available_stores()
        store_list = "\n".join([f"• {store}" for store in stores])
        
        embed = discord.Embed(
            title="🏪 Available Stores for Filtering",
            description=f"Use these store names with commands like `!search_deals 50 10 Steam`\n\n{store_list}",
            color=0x3498DB
        )
        embed.set_footer(text="Store names are case-insensitive and support partial matching")
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['store_deals'])
    async def deals_by_store(self, ctx: commands.Context, *, store_name: str):
        """Find quality game deals from a specific store
        Usage: !deals_by_store Steam
        Usage: !deals_by_store Epic Game Store
        """
        await self._search_deals_internal(ctx, min_discount=20, limit=15, store=store_name, quality_filter=True)
    
    @commands.command()
    async def test_api(self, ctx: commands.Context):
        """Test the ITAD API connection and quality filtering"""
        if not self.bot.itad_client:
            await ctx.send("❌ ITAD API not configured.")
            return
            
        try:
            # Test API with and without quality filtering
            await ctx.send("🔄 Testing API and quality filtering...")
            
            # Get all deals
            all_deals = await self.bot.itad_client.fetch_deals(
                min_discount=10, 
                limit=20, 
                log_full_response=False,
                quality_filter=False
            )
            
            # Get quality deals only
            quality_deals = await self.bot.itad_client.fetch_deals(
                min_discount=10, 
                limit=20, 
                log_full_response=False,
                quality_filter=True
            )
            
            if all_deals or quality_deals:
                embed = discord.Embed(
                    title="🧪 API & Quality Filter Test Results",
                    color=0x00ff00
                )
                
                embed.add_field(
                    name="📊 Results Summary",
                    value=f"• All deals found: **{len(all_deals)}**\n• Quality games found: **{len(quality_deals)}**\n• Filtered out: **{len(all_deals) - len(quality_deals)}**",
                    inline=False
                )
                
                if quality_deals:
                    sample_games = "\n".join([f"• {deal['title'][:40]}{'...' if len(deal['title']) > 40 else ''}" for deal in quality_deals[:5]])
                    embed.add_field(
                        name="🎮 Sample Quality Games",
                        value=sample_games,
                        inline=False
                    )
                
                if len(all_deals) > len(quality_deals):
                    filtered_deals = [deal for deal in all_deals if deal not in quality_deals]
                    sample_filtered = "\n".join([f"• {deal['title'][:40]}{'...' if len(deal['title']) > 40 else ''}" for deal in filtered_deals[:3]])
                    embed.add_field(
                        name="🚫 Sample Filtered Items",
                        value=sample_filtered + f"\n... and {len(filtered_deals) - 3} more" if len(filtered_deals) > 3 else sample_filtered,
                        inline=False
                    )
                
                embed.set_footer(text="✅ API working! Quality filter is active by default.")
                await ctx.send(embed=embed)
            else:
                await ctx.send("⚠️ API connected but no deals found")
                
        except Exception as e:
            await ctx.send(f"❌ API test failed: {str(e)}")
    
    @commands.command(aliases=['filter_help'])
    async def filtering_help(self, ctx: commands.Context):
        """Show information about quality filtering system"""
        embed = discord.Embed(
            title="🎯 Quality Game Filtering Guide",
            description="GameDealer uses smart filtering to show you actual games instead of courses and tutorials.",
            color=0x3498DB
        )
        
        embed.add_field(
            name="🎮 Commands with Quality Filtering",
            value="• `!search_deals` - Quality games (default)\n• `!quality_deals` - Quality games (explicit)\n• `!top_deals` - Top quality games\n• `!deals_by_store` - Quality games from store",
            inline=False
        )
        
        embed.add_field(
            name="📚 Commands without Filtering",
            value="• `!search_all_deals` - All deals including courses\n• Use these to see everything if needed",
            inline=False
        )
        
        embed.add_field(
            name="🚫 What Gets Filtered Out",
            value="• Programming courses & tutorials\n• Software training\n• Educational content\n• Non-game digital products\n• Low-quality/unknown stores",
            inline=False
        )
        
        embed.add_field(
            name="✅ What Stays In",
            value="• Actual video games\n• Game DLCs & expansions\n• Game soundtracks\n• From quality gaming stores\n• All price ranges (no price filtering)",
            inline=False
        )
        
        embed.set_footer(text="Quality filtering helps you find amazing game deals faster!")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Deals(bot))