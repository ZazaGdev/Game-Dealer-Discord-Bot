"""
Moderation cog for handling message filtering and moderation features.
This cog contains message filtering, word detection, and other moderation tools.
"""

import discord
from discord.ext import commands
from config import BotConfig
from utils.message_utils import should_filter_message, create_warning_embed

class Moderation(commands.Cog):
    """Moderation features and message filtering."""
    
    def __init__(self, bot):
        self.bot = bot
        self.filtered_words = BotConfig.FILTERED_WORDS
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle message filtering and moderation."""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Check if message should be filtered
        if should_filter_message(message.content, self.filtered_words):
            try:
                # Delete the message
                await message.delete()
                
                # Send warning
                embed = create_warning_embed(
                    message.author,
                    "Your message contained inappropriate content and was removed."
                )
                
                warning_msg = await message.channel.send(embed=embed)
                
                # Delete warning after 5 seconds
                await warning_msg.delete(delay=5)
                
                print(f"🛡️ Filtered message from {message.author.name}: {message.content}")
                
            except discord.NotFound:
                # Message was already deleted
                pass
            except discord.Forbidden:
                print(f"❌ Missing permissions to delete message from {message.author.name}")
            except Exception as e:
                print(f"❌ Error handling filtered message: {e}")
    
    @commands.command(name='filter', help='Add or remove words from the filter')
    @commands.has_permissions(manage_messages=True)
    async def filter_word(self, ctx, action: str, *, word: str = None):
        """Add or remove words from the message filter."""
        if action.lower() == 'add' and word:
            if word.lower() not in [w.lower() for w in self.filtered_words]:
                self.filtered_words.append(word.lower())
                await ctx.send(f"✅ Added `{word}` to the filter list.")
            else:
                await ctx.send(f"⚠️ `{word}` is already in the filter list.")
        
        elif action.lower() == 'remove' and word:
            original_count = len(self.filtered_words)
            self.filtered_words = [w for w in self.filtered_words if w.lower() != word.lower()]
            
            if len(self.filtered_words) < original_count:
                await ctx.send(f"✅ Removed `{word}` from the filter list.")
            else:
                await ctx.send(f"⚠️ `{word}` was not found in the filter list.")
        
        elif action.lower() == 'list':
            if self.filtered_words:
                word_list = ", ".join([f"`{word}`" for word in self.filtered_words])
                embed = discord.Embed(
                    title="🛡️ Filtered Words",
                    description=word_list,
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("📝 No words are currently being filtered.")
        
        else:
            await ctx.send(f"❌ Usage: `{BotConfig.COMMAND_PREFIX}filter <add|remove|list> [word]`")

async def setup(bot):
    """Required function to load the cog."""
    await bot.add_cog(Moderation(bot))
    print("✅ Moderation cog loaded")