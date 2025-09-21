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
        Search for deals with custom filters
        Usage: !search_deals 70 15
        Usage: !search_deals 50 10 Steam
        Usage: !search_deals 60 5 Epic Game Store
        """
        if not self.bot.itad_client:
            await ctx.send("❌ ITAD API not configured. Please check your API key.")
            return
        
        if limit > 25:
            limit = 25
            await ctx.send("⚠️ Limit capped at 25 deals.")
        
        # Build search message
        search_text = f"🔍 Searching for {limit} deals with minimum {min_discount}% discount"
        if store:
            search_text += f" from **{store}**"
        search_text += "..."
        
        search_msg = await ctx.send(search_text)
        
        try:
            deals = await self.bot.itad_client.fetch_deals(
                min_discount=min_discount,
                limit=limit,
                store_filter=store,
                log_full_response=True  # Always log full response for Discord commands
            )
            
            if not deals:
                error_msg = f"❌ No deals found with {min_discount}% minimum discount"
                if store:
                    error_msg += f" from **{store}**"
                    error_msg += f"\n💡 Try:\n• Lower discount threshold (e.g., `!search_deals 10 10 {store}`)\n• Different store (`!list_stores` to see available)\n• Remove store filter (`!search_deals {min_discount} {limit}`)"
                else:
                    error_msg += f"\n💡 Try lowering the discount threshold (e.g., `!search_deals 10 {limit}`)"
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
                    title=f"🎮 Found {len(deals)} Great Deals!" + (f" (Page {page_num}/{total_pages})" if total_pages > 1 else ""),
                    description=f"Minimum discount: {min_discount}%" + (f" • Store: **{store}**" if store else ""),
                    color=0x00ff00,
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
                    embed.set_footer(text="Use !post_best to share the top deal" + (f" • {total_pages} pages total" if total_pages > 1 else ""))
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
        """Get top deals quickly with optional store filter"""
        await self.search_deals.invoke(ctx, min_discount=30, limit=count, store=store)
    
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
        """Find deals from a specific store
        Usage: !deals_by_store Steam
        Usage: !deals_by_store Epic Game Store
        """
        await self.search_deals.invoke(ctx, min_discount=20, limit=15, store=store_name)
    
    @commands.command()
    async def test_api(self, ctx: commands.Context):
        """Test the ITAD API connection"""
        if not self.bot.itad_client:
            await ctx.send("❌ ITAD API not configured.")
            return
            
        try:
            # Test basic API call
            deals = await self.bot.itad_client.fetch_deals(
                min_discount=10, 
                limit=3, 
                log_full_response=False
            )
            
            if deals:
                msg = f"✅ API working! Found {len(deals)} deals:\n"
                for i, deal in enumerate(deals[:3]):
                    msg += f"{i+1}. {deal['title'][:30]} at {deal['store']} ({deal.get('discount', 'N/A')})\n"
                await ctx.send(msg)
            else:
                await ctx.send("⚠️ API connected but no deals found")
                
        except Exception as e:
            await ctx.send(f"❌ API test failed: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Deals(bot))