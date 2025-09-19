"""
Member events cog for handling member-related Discord events.
This cog handles member joins, leaves, and other member events.
"""

import discord
from discord.ext import commands
from config import BotConfig

class MemberEvents(commands.Cog):
    """Handles member-related events."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle when a new member joins the server."""
        if not BotConfig.WELCOME_NEW_MEMBERS:
            return
        
        # Send welcome message to the member
        try:
            embed = discord.Embed(
                title="🎉 Welcome to the Server!",
                description=f"Welcome to **{member.guild.name}**, {member.mention}!",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Getting Started", 
                value=f"Use `{BotConfig.COMMAND_PREFIX}help` to see available commands!",
                inline=False
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"You are member #{member.guild.member_count}")
            
            await member.send(embed=embed)
            print(f"✅ Sent welcome message to {member.name}")
            
        except discord.Forbidden:
            print(f"❌ Could not send welcome message to {member.name} (DMs disabled)")
        except Exception as e:
            print(f"❌ Error sending welcome message to {member.name}: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Handle when a member leaves the server."""
        print(f"👋 {member.name} left the server: {member.guild.name}")
        
        # You could add logging to a channel here
        # For example, send a message to a log channel about the member leaving

async def setup(bot):
    """Required function to load the cog."""
    await bot.add_cog(MemberEvents(bot))
    print("✅ Member events cog loaded")