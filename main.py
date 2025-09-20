# main.py (only the parts that change)
import os
import logging
from config.logging_config import setup_logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncio

from bot import create_bot  # <-- NEW

# --- config & logging ---
load_dotenv()
setup_logging()
TOKEN = os.getenv("DISCORD_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
DEALS_CHANNEL_ID = int(os.getenv("DEALS_CHANNEL_ID", LOG_CHANNEL_ID))

log = logging.getLogger("GameDealer")
app = FastAPI()

# --- create the bot from our core module ---
bot = create_bot(
    log=log,
    log_channel_id=LOG_CHANNEL_ID,
    deals_channel_id=DEALS_CHANNEL_ID,
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
            asyncio.create_task(bot.send_deal(deal_data))  # <-- use the bot API
        else:
            log.error("Bot event loop not available")

        return JSONResponse({"status": "deal_processed"}, status_code=200)

    else:
        return JSONResponse({"status": "unknown_event"}, status_code=200)

# --- run uvicorn in a thread, then bot.run(TOKEN) as before ---
