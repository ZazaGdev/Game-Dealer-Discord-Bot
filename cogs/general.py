# cogs/general.py
import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import make_startup_embed

class General(commands.Cog):
    """Essential utility commands for GameDealer bot"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = getattr(bot, 'log', None)
        self.log_channel_id = getattr(bot, 'log_channel_id', 0)
        self.bot_ready = False
        self._announced_once = False

    # --- listeners ---
    @commands.Cog.listener()
    async def on_ready(self):
        if self._announced_once:
            return
        self._announced_once = True
        self.bot_ready = True

        if self.log:
            self.log.info(f"Logged in as {self.bot.user} (id={self.bot.user.id})")

        if not self.log_channel_id:
            if self.log:
                self.log.warning("LOG_CHANNEL_ID not set; skipping startup message.")
            return

        channel = self.bot.get_channel(self.log_channel_id)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(self.log_channel_id)
            except Exception as e:
                if self.log:
                    self.log.error(f"Could not fetch channel {self.log_channel_id}: {e}")
                return

        try:
            await channel.send(embed=make_startup_embed(self.bot.user))
            if self.log:
                self.log.info(f"Startup message sent to channel {getattr(channel, 'name', self.log_channel_id)}")
        except discord.Forbidden:
            if self.log:
                self.log.error("Missing permissions to send messages in the target channel.")
        except Exception as e:
            if self.log:
                self.log.exception(f"Failed to send startup message: {e}")

    # --- essential commands ---
    @app_commands.command(name="ping", description="Test bot responsiveness")
    async def ping(self, interaction: discord.Interaction):
        """Test bot responsiveness"""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms")

    @app_commands.command(name="help", description="Show available commands")
    async def help(self, interaction: discord.Interaction):
        """Show available commands"""
        embed = discord.Embed(
            title="🎮 GameDealer Commands",
            description="Find the best game deals from Steam, Epic & GOG!",
            color=0x00ff00
        )
        
        embed.add_field(
            name="📊 Deal Commands",
            value="• `/search_deals [amount]` - Best deals from Steam, Epic & GOG\n• `/search_store [store] [amount]` - Deals from specific store",
            inline=False
        )
        
        embed.add_field(
            name="💡 Examples",
            value="• `/search_deals 15` - Get 15 best deals\n• `/search_store Steam 20` - Get 20 Steam deals\n• `/search_store Epic 10` - Get 10 Epic deals",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Utility",
            value="• `/ping` - Test bot response\n• `/info` - Bot information",
            inline=False
        )
        
        embed.set_footer(text="🎯 Deals are automatically sorted by highest discount percentage")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="Show bot information")
    async def info(self, interaction: discord.Interaction):
        """Show bot information"""
        embed = discord.Embed(
            title="🤖 GameDealer Bot Info",
            description="Your source for the best game deals!",
            color=0x00ff00
        )
        
        # Get database stats if available
        try:
            if hasattr(self.bot, 'itad_client') and self.bot.itad_client:
                stats = self.bot.itad_client.priority_filter.get_database_stats()
                embed.add_field(
                    name="📚 Game Database", 
                    value=f"{stats['total_games']} curated games", 
                    inline=True
                )
        except:
            pass
        
        embed.add_field(name="🎯 Supported Stores", value="Steam, Epic, GOG + more", inline=True)
        embed.add_field(name="🏓 Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="🤖 Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="👥 Users", value=sum(g.member_count for g in self.bot.guilds if g.member_count), inline=True)
        embed.add_field(name="⚡ Commands", value=len(self.bot.tree.get_commands()), inline=True)
        
        embed.set_footer(text=f"Requested by {interaction.user}")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))