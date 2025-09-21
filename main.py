# main.py - Simplified for scheduled requests with timer system
import os
import asyncio
import logging
from dotenv import load_dotenv
from config.app_config import load_config
from config.logging_config import setup_logging
from bot.core import create_bot

async def main():
    """Main entry point for scheduled deal fetching (no webhooks)"""
    # Load environment variables
    load_dotenv()
    
    # Initialize config
    config = load_config()
    
    # Setup logging using config module
    log = setup_logging(level=logging.INFO)
    
    log.info("Starting GameDealer bot (scheduled mode with timer system)...")
    
    # Validate configuration
    if not config.discord_token:
        log.error("DISCORD_TOKEN is missing in your environment (.env).")
        return
    
    if not config.itad_api_key:
        log.warning("ITAD_API_KEY is missing. Deal fetching will not work.")
    
    # Initialize bot
    bot = create_bot(
        log=log,
        log_channel_id=config.log_channel_id,
        deals_channel_id=config.deals_channel_id,
        itad_api_key=config.itad_api_key
    )
    
    try:
        # Load the scheduler cog for automated deal posting
        await bot.load_extension('bot.scheduler')
        log.info("Deal scheduler loaded successfully - daily deals at 9 AM")
        
        # Start the bot (this blocks until bot stops)
        await bot.start(config.discord_token)
    except KeyboardInterrupt:
        log.info("Bot shutdown requested by user")
    except asyncio.CancelledError:
        log.info("Bot shutdown - operation cancelled")
    except Exception as e:
        log.error(f"Bot error: {e}")
    finally:
        # Ensure proper cleanup
        if not bot.is_closed():
            await bot.close()
        log.info("Bot shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
