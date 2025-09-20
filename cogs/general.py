# cogs/core.py
import discord
from discord.ext import commands
from utils.embeds import make_startup_embed, make_deal_embed

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # quick aliases to values you set on bot in main.py
        self.log = bot.log
        self.deals_channel_id = bot.deals_channel_id
        self.log_channel_id = bot.log_channel_id
        self.bot_ready = False

    # --- listeners ---
    @commands.Cog.listener()
    async def on_ready(self):
        if getattr(self, "_announced_once", False):
            return
        self._announced_once = True
        self.bot_ready = True

        self.log.info(f"Logged in as {self.bot.user} (id={self.bot.user.id})")

        if not self.log_channel_id:
            self.log.warning("LOG_CHANNEL_ID not set; skipping startup message.")
            return

        channel = self.bot.get_channel(self.log_channel_id)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(self.log_channel_id)
            except Exception as e:
                self.log.error(f"Could not fetch channel {self.log_channel_id}: {e}")
                return

        try:
            await channel.send(embed=make_startup_embed(self.bot.user))
            self.log.info(f"Startup message sent to channel {getattr(channel, 'name', self.log_channel_id)}")
        except discord.Forbidden:
            self.log.error("Missing permissions to send messages in the target channel.")
        except Exception as e:
            self.log.exception(f"Failed to send startup message: {e}")

    # --- commands ---
    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("Pong!")

    @commands.command()
    async def deals(self, ctx: commands.Context):
        await ctx.send("Here are today's game deals!")

    @commands.command()
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
        await ctx.send("✅ Test deal sent successfully!" if success else "❌ Failed to send test deal. Check logs for details.")

    # --- helper used by webhook & commands ---
    async def send_deal_to_discord(self, deal_data: dict) -> bool:
        if not self.bot_ready:
            self.log.warning("Bot not ready, cannot send Discord message")
            return False

        channel_id = self.deals_channel_id or self.log_channel_id
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception as e:
                self.log.error(f"Could not fetch deals channel {channel_id}: {e}")
                return False

        try:
            embed = make_deal_embed(deal_data)
            await channel.send(embed=embed)
            self.log.info(f"Deal message sent to channel {getattr(channel, 'name', channel_id)}")
            return True
        except discord.Forbidden:
            self.log.error("Missing permissions to send messages in the deals channel.")
            return False
        except Exception as e:
            self.log.exception(f"Failed to send deal message: {e}")
            return False


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
