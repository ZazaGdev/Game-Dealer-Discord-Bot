"""
Core bot module containing the main GameDealer bot class.
This module handles bot initialization, cog loading, and core functionality.
"""

import discord
from discord.ext import commands
import logging
import asyncio
from pathlib import Path
from typing import Optional
import traceback

from config import BotConfig

class GameDealerBot(commands.Bot):
    """Custom bot class for the GameDealer Discord bot."""
    
    def __init__(self):
        # Setup intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        # Initialize the bot
        super().__init__(
            command_prefix=BotConfig.COMMAND_PREFIX,
            intents=intents,
            help_command=None  # We'll create a custom help command later
        )
        
        # Bot state
        self.initial_extensions = []
        
    async def setup_hook(self):
        """Called when the bot is starting up."""
        print("Setting up bot...")
        
        # Load all cogs
        await self.load_cogs()
        
        print(f"Bot setup completed. Loaded {len(self.cogs)} cogs.")
    
    async def load_cogs(self):
        """Load all cog files from the cogs directory."""
        cogs_dir = Path("cogs")
        
        if not cogs_dir.exists():
            print("Cogs directory not found!")
            return
        
        # Load all Python files in the cogs directory
        for file_path in cogs_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue  # Skip files starting with underscore
                
            cog_name = f"cogs.{file_path.stem}"
            
            try:
                await self.load_extension(cog_name)
                print(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                print(f"❌ Failed to load cog {cog_name}: {e}")
                traceback.print_exc()
    
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        print(f"🤖 {self.user.name} is ready and online!")
        print(f"📊 Connected to {len(self.guilds)} guild(s)")
        print(f"👥 Serving {len(set(self.get_all_members()))} unique users")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name=f"Use {BotConfig.COMMAND_PREFIX}help")
        )
    
    async def on_command_error(self, ctx, error):
        """Global error handler for commands."""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
        
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument provided!")
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")
        
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to execute this command!")
        
        else:
            # Log unexpected errors
            print(f"Unexpected error in command {ctx.command}: {error}")
            traceback.print_exc()
            await ctx.send("❌ An unexpected error occurred!")
    
    async def close(self):
        """Clean shutdown of the bot."""
        print("🔄 Shutting down bot...")
        await super().close()

async def create_bot() -> GameDealerBot:
    """Factory function to create and return a bot instance."""
    # Validate configuration
    BotConfig.validate_config()
    
    # Create bot instance
    bot = GameDealerBot()
    
    return bot