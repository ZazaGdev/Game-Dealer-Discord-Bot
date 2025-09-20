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
    async def search_deals(self, ctx: commands.Context, min_discount: int = 50, limit: int = 10):
        """
        Search for deals with custom filters
        Usage: !search_deals 70 15
        """
        if not self.bot.itad_client:
            await ctx.send("❌ ITAD API not configured. Please check your API key.")
            return
        
        if limit > 25:
            limit = 25
            await ctx.send("⚠️ Limit capped at 25 deals.")
        
        # Send initial message
        search_msg = await ctx.send(f"🔍 Searching for {limit} deals with minimum {min_discount}% discount...")
        
        try:
            deals = await self.bot.itad_client.fetch_deals(
                min_discount=min_discount,
                limit=limit
            )
            
            if not deals:
                await search_msg.edit(content=f"❌ No deals found with {min_discount}% minimum discount")
                return
            
            # Create a comprehensive embed showing multiple deals
            embed = discord.Embed(
                title=f"🎮 Found {len(deals)} Great Deals!",
                description=f"Minimum discount: {min_discount}%",
                color=0x00ff00,
                timestamp=ctx.message.created_at
            )
            
            # Add top deals as fields
            for i, deal in enumerate(deals[:10]):  # Show max 10 in embed
                discount_text = f" ({deal.get('discount', 'N/A')})" if deal.get('discount') else ""
                value = f"**{deal['price']}** at {deal['store']}{discount_text}"
                
                if deal.get('url'):
                    value += f"\n[🔗 Get Deal]({deal['url']})"
                
                embed.add_field(
                    name=f"{i+1}. {deal['title'][:45]}{'...' if len(deal['title']) > 45 else ''}",
                    value=value,
                    inline=False
                )
            
            embed.set_footer(text="Use !post_best to share the top deal")
            
            # Edit the original message with results
            await search_msg.edit(content="✅ Search completed!", embed=embed)
            
            # Store deals for other commands to use
            self.bot._last_deals = deals
            
        except ValueError as e:
            await search_msg.edit(content=f"❌ Configuration error: {str(e)}")
        except Exception as e:
            if self.log:
                self.log.error(f"Error searching deals: {e}")
            await search_msg.edit(content=f"❌ Error occurred while searching for deals: {str(e)}")
    
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
    async def top_deals(self, ctx: commands.Context, count: int = 5):
        """Get top deals quickly"""
        await self.search_deals.invoke(ctx, min_discount=60, limit=count)

async def setup(bot: commands.Bot):
    await bot.add_cog(Deals(bot))