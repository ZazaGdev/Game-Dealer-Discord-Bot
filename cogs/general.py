"""
General commands cog for basic bot functionality.
This cog contains simple commands like hello, ping, etc.
"""

import discord
from discord.ext import commands
from config import BotConfig

class GeneralCommands(commands.Cog):
    """General purpose commands for the bot."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='hello', help='Greet a user')
    async def hello(self, ctx):
        """Greet the user who called the command."""
        embed = discord.Embed(
            title="👋 Hello!",
            description=f"Hello {ctx.author.mention}! Nice to meet you!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
    
    @commands.command(name='ping', help='Check bot latency')
    async def ping(self, ctx):
        """Check the bot's latency."""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: {latency}ms",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='info', help='Get bot information')
    async def info(self, ctx):
        """Display information about the bot."""
        embed = discord.Embed(
            title="🤖 Bot Information",
            color=discord.Color.purple()
        )
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(set(self.bot.get_all_members())), inline=True)
        embed.add_field(name="Prefix", value=BotConfig.COMMAND_PREFIX, inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Required function to load the cog."""
    await bot.add_cog(GeneralCommands(bot))
    print("✅ General commands cog loaded")