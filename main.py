# main.py
import os
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import threading

# ---------- Config & logging ----------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
DEALS_CHANNEL_ID = int(os.getenv("DEALS_CHANNEL_ID", LOG_CHANNEL_ID))  # Add this to your .env

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    handlers=[logging.FileHandler("discord.log", encoding="utf-8"), logging.StreamHandler()],
)

log = logging.getLogger("GameDealer")
app = FastAPI() 

# ---------- Bot setup ----------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

_announced_once = False
bot_ready = False  # Track if bot is ready

def make_startup_embed(user: discord.abc.User) -> discord.Embed:
    e = discord.Embed(
        title="✅ Bot online",
        description="GameDealer is running and ready to post deals.",
        timestamp=datetime.now(timezone.utc),
        color=0x00ff00
    )
    e.set_footer(text=f"Logged in as {user}")
    return e

def make_deal_embed(deal_data: dict) -> discord.Embed:
    """Create an embed for game deals"""
    title = deal_data.get("title", "Game Deal")
    price = deal_data.get("price", "Unknown")
    store = deal_data.get("store", "Unknown Store")
    url = deal_data.get("url", "")
    
    embed = discord.Embed(
        title=f"🎮 {title}",
        description=f"**Price:** {price}\n**Store:** {store}",
        color=0xff6b35,
        timestamp=datetime.now(timezone.utc)
    )
    
    if url:
        embed.add_field(name="Link", value=f"[Get Deal]({url})", inline=False)
    
    embed.set_footer(text="Powered by IsThereAnyDeal")
    return embed

@bot.event
async def on_ready():
    global _announced_once, bot_ready
    if _announced_once:
        return
    _announced_once = True
    bot_ready = True

    log.info(f"Logged in as {bot.user} (id={bot.user.id})")

    if not LOG_CHANNEL_ID:
        log.warning("LOG_CHANNEL_ID not set; skipping startup message.")
        return

    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(LOG_CHANNEL_ID)
        except Exception as e:
            log.error(f"Could not fetch channel {LOG_CHANNEL_ID}: {e}")
            return

    try:
        await channel.send(embed=make_startup_embed(bot.user))
        log.info(f"Startup message sent to channel {getattr(channel, 'name', LOG_CHANNEL_ID)}")
    except discord.Forbidden:
        log.error("Missing permissions to send messages in the target channel.")
    except Exception as e:
        log.exception(f"Failed to send startup message: {e}")

# Commands
@bot.command()
async def ping(ctx: commands.Context):
    await ctx.send("Pong!")

@bot.command()
async def deals(ctx: commands.Context):
    await ctx.send("Here are today's game deals!")

@bot.command()
async def test_deal(ctx: commands.Context):
    """Test the send_deal_to_discord function with sample data"""
    test_data = {
        "title": "Cyberpunk 2077",
        "price": "$19.99",
        "store": "Steam",
        "url": "https://store.steampowered.com/app/1091500/Cyberpunk_2077/",
        "discount": "67%",
        "original_price": "$59.99"
    }
    
    await ctx.send("🔄 Sending test deal...")
    success = await send_deal_to_discord(test_data)
    
    if success:
        await ctx.send("✅ Test deal sent successfully!")
    else:
        await ctx.send("❌ Failed to send test deal. Check logs for details.")

# Function to send Discord message from webhook
async def send_deal_to_discord(deal_data: dict):
    """Send a deal message to Discord channel"""
    if not bot_ready:
        log.warning("Bot not ready, cannot send Discord message")
        return False
    
    channel_id = DEALS_CHANNEL_ID or LOG_CHANNEL_ID
    channel = bot.get_channel(channel_id)
    
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception as e:
            log.error(f"Could not fetch deals channel {channel_id}: {e}")
            return False
    
    try:
        embed = make_deal_embed(deal_data)
        await channel.send(embed=embed)
        log.info(f"Deal message sent to channel {getattr(channel, 'name', channel_id)}")
        return True
    except discord.Forbidden:
        log.error("Missing permissions to send messages in the deals channel.")
        return False
    except Exception as e:
        log.exception(f"Failed to send deal message: {e}")
        return False

@app.post("/itad-webhook")
async def itad_webhook(request: Request):
    headers = request.headers
    user_agent = headers.get("User-Agent")
    event = headers.get("ITAD-Event")
    hook_id = headers.get("ITAD-Hook-ID")
    
    try:
        body = await request.json()
    except Exception as e:
        log.error(f"Failed to parse webhook body: {e}")
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    log.info(f"Received ITAD webhook: event={event}, hook_id={hook_id}")
    
    # Handle different ITAD events
    if event == "ping":
        log.info("ITAD ping received")
        return JSONResponse({"status": "pong"}, status_code=200)
    
    elif event == "deal":
        # Process deal data
        deal_data = {
            "title": body.get("title", "Unknown Game"),
            "price": body.get("price", "Unknown"),
            "store": body.get("store", "Unknown Store"),
            "url": body.get("url", ""),
            "discount": body.get("discount", ""),
            "original_price": body.get("original_price", "")
        }
        
        # Send to Discord (run in bot's event loop)
        if bot.loop and bot.loop.is_running():
            asyncio.create_task(send_deal_to_discord(deal_data))
        else:
            log.error("Bot event loop not available")
            
        log.info(f"Deal processed: {deal_data['title']}")
        return JSONResponse({"status": "deal_processed"}, status_code=200)
    
    else:
        log.warning(f"Unknown ITAD event: {event}")
        return JSONResponse({"status": "unknown_event"}, status_code=200)

# Run FastAPI in a separate thread
def run_fastapi():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN is missing in your environment (.env).")
    
    # Start FastAPI server in background thread
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    log.info("Starting Discord bot...")
    log.info("FastAPI webhook server running on http://0.0.0.0:8000")
    
    # Run Discord bot (blocking)
    bot.run(TOKEN)