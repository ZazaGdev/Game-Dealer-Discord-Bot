# main.py - Simplified for scheduled requests with timer system
import os
import asyncio
import logging
import sys
from typing import NoReturn, Optional
from dotenv import load_dotenv
from config.app_config import load_config, ConfigError
from config.logging_config import setup_logging
from bot.core import create_bot

async def main() -> None:
    """Main entry point for scheduled deal fetching with enhanced error handling"""
    # Load environment variables
    load_dotenv()
    
    # Setup logging first
    log: logging.Logger = setup_logging(level=logging.INFO)
    
    try:
        # Initialize config with validation
        config = load_config()
        config.validate()
    except ConfigError as e:
        log.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        log.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    log.info("Starting GameDealer bot (scheduled mode with timer system)...")
    
    # Warn about missing ITAD API key but don't exit
    if not config.itad_api_key:
        log.warning("ITAD_API_KEY is missing. Deal fetching will not work.")
    
    # Initialize bot
    bot = create_bot(
        log=log,
        log_channel_id=config.log_channel_id,
        deals_channel_id=config.deals_channel_id,
        itad_api_key=config.itad_api_key
    )
    
    bot: Optional[object] = None
    try:
        # Create and run bot
        bot = create_bot(
            log=log,
            log_channel_id=config.log_channel_id, 
            deals_channel_id=config.deals_channel_id,
            itad_api_key=config.itad_api_key
        )
        
        await bot.start(config.discord_token)
    except KeyboardInterrupt:
        log.info("Bot stopped by user.")
    except Exception as e:
        log.error(f"Bot crashed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Ensure proper cleanup
        if not bot.is_closed():
            await bot.close()
        log.info("Bot shutdown complete")

def run_bot() -> NoReturn:
    """Run the bot with proper exception handling"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
