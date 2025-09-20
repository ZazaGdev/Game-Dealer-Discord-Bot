# main.py (complete version)
import os
import logging
import threading
from config.logging_config import setup_logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncio

from bot import create_bot 

# --- config & logging ---
load_dotenv()
setup_logging()

TOKEN = os.getenv("DISCORD_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
DEALS_CHANNEL_ID = int(os.getenv("DEALS_CHANNEL_ID", LOG_CHANNEL_ID))
ITAD_API_KEY = os.getenv("ITAD_API_KEY")

log = logging.getLogger("GameDealer")
app = FastAPI()

# --- create the bot from our core module ---
bot = create_bot(
    log=log,
    log_channel_id=LOG_CHANNEL_ID,
    deals_channel_id=DEALS_CHANNEL_ID,
    itad_api_key=ITAD_API_KEY
)

# --- FastAPI webhook ---
@app.post("/itad-webhook")
async def itad_webhook(request: Request):
    headers = request.headers
    event = headers.get("ITAD-Event")
    hook_id = headers.get("ITAD-Hook-ID")

    try:
        body = await request.json()
    except Exception as e:
        log.error(f"Failed to parse webhook body: {e}")
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    log.info(f"Received ITAD webhook: event={event}, hook_id={hook_id}")

    if event == "ping":
        return JSONResponse({"status": "pong"}, status_code=200)

    elif event == "deal":
        deal_data = {
            "title": body.get("title", "Unknown Game"),
            "price": body.get("price", "Unknown"),
            "store": body.get("store", "Unknown Store"),
            "url": body.get("url", ""),
            "discount": body.get("discount", ""),
            "original_price": body.get("original_price", ""),
        }

        if bot.loop and bot.loop.is_running():
            asyncio.create_task(bot.send_deal(deal_data))
        else:
            log.error("Bot event loop not available")

        return JSONResponse({"status": "deal_processed"}, status_code=200)

    else:
        return JSONResponse({"status": "unknown_event"}, status_code=200)

# --- run uvicorn in a thread, then bot.run(TOKEN) as before ---
def run_fastapi():
    """Run FastAPI server in a separate thread"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

def main():
    """Main entry point"""
    if not TOKEN:
        log.error("DISCORD_TOKEN is missing in your environment (.env).")
        return
    
    # Start FastAPI server in background thread
    log.info("Starting FastAPI webhook server...")
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Start Discord bot (blocking)
    log.info("Starting Discord bot...")
    log.info("FastAPI webhook server running on http://0.0.0.0:8000")
    
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        log.info("Bot stopped by user")
    except Exception as e:
        log.error(f"Error running bot: {e}")

if __name__ == "__main__":
    main()