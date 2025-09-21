# bot/scheduler.py - Handle scheduled deal fetching
import asyncio
import logging
from datetime import datetime, time
from typing import Optional
from discord.ext import tasks, commands

class DealScheduler:
    """Handle scheduled deal fetching and posting"""
    
    def __init__(self, bot, log: logging.Logger):
        self.bot = bot
        self.log = log
        self.daily_deals_enabled = True
        self.last_deal_time = None  # Track last execution to prevent rapid repeats
        
    def start_scheduler(self):
        """Start the scheduled tasks"""
        if not self.daily_deals.is_running():
            self.daily_deals.start()
            self.log.info("Deal scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduled tasks"""
        if self.daily_deals.is_running():
            self.daily_deals.cancel()
            self.log.info("Deal scheduler stopped")
    
    @tasks.loop(time=time(hour=9, minute=0))  # 9 AM daily
    async def daily_deals(self):
        """Fetch and post daily deals"""
        if not self.daily_deals_enabled:
            return
            
        # Prevent rapid execution (minimum 23 hours between runs)
        from datetime import datetime, timedelta
        now = datetime.now()
        if self.last_deal_time and (now - self.last_deal_time) < timedelta(hours=23):
            self.log.debug(f"Skipping daily deal fetch - last run was {self.last_deal_time}")
            return
            
        self.last_deal_time = now
        self.log.info("Starting daily deal fetch...")
        
        try:
            if not self.bot.itad_client:
                self.log.error("ITAD client not available for daily deals")
                return
            
            # Fetch good deals (60% discount minimum) with full response logging
            deals = await self.bot.itad_client.fetch_deals(
                min_discount=30,  # Lower threshold to find more deals
                limit=10,
                log_full_response=True  # Log daily scheduled fetches too
            )
            
            if not deals:
                self.log.info("No deals found for daily posting")
                return
            
            # Post the best deal to Discord
            best_deal = deals[0]
            general_cog = self.bot.get_cog("General")
            
            if general_cog:
                success = await general_cog.send_deal_to_discord(best_deal)
                if success:
                    self.log.info(f"Posted daily deal: {best_deal['title']}")
                else:
                    self.log.error("Failed to post daily deal")
            else:
                self.log.error("General cog not found for daily deal posting")
                
        except Exception as e:
            self.log.error(f"Error in daily deal fetch: {e}")
    
    @daily_deals.before_loop
    async def before_daily_deals(self):
        """Wait for bot to be ready before starting scheduled tasks"""
        await self.bot.wait_until_ready()
        self.log.info("Bot ready, daily deal scheduler initialized")

# Add scheduler commands to a cog
class SchedulerCommands(commands.Cog):
    """Commands to control the deal scheduler"""
    
    def __init__(self, bot):
        self.bot = bot
        self.log = getattr(bot, 'log', logging.getLogger(__name__))
        self.scheduler = DealScheduler(bot, self.log)
        
    async def cog_load(self):
        """Start scheduler when cog loads"""
        self.scheduler.start_scheduler()
    
    async def cog_unload(self):
        """Stop scheduler when cog unloads"""
        self.scheduler.stop_scheduler()
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def enable_daily_deals(self, ctx):
        """Enable daily deal posting"""
        self.scheduler.daily_deals_enabled = True
        await ctx.send("✅ Daily deal posting enabled")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disable_daily_deals(self, ctx):
        """Disable daily deal posting"""
        self.scheduler.daily_deals_enabled = False
        await ctx.send("❌ Daily deal posting disabled")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def trigger_daily_deals(self, ctx):
        """Manually trigger daily deal posting"""
        await ctx.send("🔄 Triggering daily deal fetch...")
        await self.scheduler.daily_deals()
        await ctx.send("✅ Daily deal fetch completed")

async def setup(bot):
    await bot.add_cog(SchedulerCommands(bot))