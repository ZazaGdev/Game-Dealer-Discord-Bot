# cogs/general.py
import discord
from discord.ext import commands
from utils.embeds import make_startup_embed, make_deal_embed

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = getattr(bot, 'log', None)
        self.deals_channel_id = getattr(bot, 'deals_channel_id', 0)
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

    # --- commands ---
    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Test bot responsiveness"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: {latency}ms")

    @commands.command(aliases=['deal'])
    async def deals(self, ctx: commands.Context):
        """Show information about game deals"""
        await ctx.send("Here are today's game deals! Use `!test_deal` to see a sample deal.")

    @commands.command(aliases=['test_deals', 'testdeal'])
    async def test_deal(self, ctx: commands.Context):
        """Test the send_deal_to_discord function with sample data"""
        test_data = {
            "title": "Cyberpunk 2077",
            "price": "$19.99",
            "store": "Steam",
            "url": "https://store.steampowered.com/app/1091500/Cyberpunk_2077/",
            "discount": "67%",
            "original_price": "$59.99",
        }

        await ctx.send("🔄 Sending test deal...")
        success = await self.send_deal_to_discord(test_data)
        
        if success:
            await ctx.send("✅ Test deal sent successfully!")
        else:
            await ctx.send("❌ Failed to send test deal. Check logs for details.")

    @commands.command()
    async def info(self, ctx: commands.Context):
        """Show bot information"""
        embed = discord.Embed(
            title="🤖 GameDealer Bot Info",
            color=0x00ff00
        )
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=sum(g.member_count for g in self.bot.guilds if g.member_count), inline=True)
        embed.add_field(name="Commands", value=len(self.bot.commands), inline=True)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    # --- helper used by webhook & commands ---
    async def send_deal_to_discord(self, deal_data: dict) -> bool:
        if not self.bot_ready:
            if self.log:
                self.log.warning("Bot not ready, cannot send Discord message")
            return False

        channel_id = self.deals_channel_id or self.log_channel_id
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception as e:
                if self.log:
                    self.log.error(f"Could not fetch deals channel {channel_id}: {e}")
                return False

        try:
            embed = make_deal_embed(deal_data)
            await channel.send(embed=embed)
            if self.log:
                self.log.info(f"Deal message sent to channel {getattr(channel, 'name', channel_id)}")
            return True
        except discord.Forbidden:
            if self.log:
                self.log.error("Missing permissions to send messages in the deals channel.")
            return False
        except Exception as e:
            if self.log:
                self.log.exception(f"Failed to send deal message: {e}")
            return False

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))