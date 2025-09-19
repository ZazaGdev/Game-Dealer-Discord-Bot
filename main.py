"""
GameDealer Discord Bot - Main Entry Point

A well-structured Discord bot for game-related functionality.
This is the main entry point that initializes and runs the bot.

Author: Your Name
Version: 1.0.0
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bot import create_bot
from config import BotConfig, setup_logging
from utils import setup_custom_logger, cleanup_old_logs

async def main():
    """Main function to initialize and run the bot."""
    try:
        # Validate configuration
        print("🔧 Validating configuration...")
        BotConfig.validate_config()
        
        # Setup logging
        print("📝 Setting up logging...")
        log_handler = setup_logging()
        logger = setup_custom_logger('GameDealerBot')
        
        # Clean up old logs
        cleanup_old_logs()
        
        # Create bot instance
        print("🤖 Creating bot instance...")
        bot = await create_bot()
        
        # Run the bot
        print("🚀 Starting bot...")
        logger.info("Bot is starting up...")
        
        async with bot:
            await bot.start(BotConfig.TOKEN)
            
    except KeyboardInterrupt:
        print("\n🛑 Bot shutdown requested by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    """Entry point when running the script directly."""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)