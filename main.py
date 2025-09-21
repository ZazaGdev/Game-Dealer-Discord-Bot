# main.py - Simplified for scheduled requests with timer system
import os
import asyncio
import logging
from dotenv import load_dotenv
from config.app_config import load_config
from bot.core import create_bot

async def main():
    """Main entry point for scheduled deal fetching (no webhooks)"""
    # Load environment variables
    load_dotenv()
    
    # Initialize config
    config = load_config()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('discord.log'),
            logging.StreamHandler()
        ]
    )
    log = logging.getLogger(__name__)
    
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
        log.info("Bot shutdown requested")
    except Exception as e:
        log.error(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
