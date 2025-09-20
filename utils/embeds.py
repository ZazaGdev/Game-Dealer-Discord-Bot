from datetime import datetime, timezone
import discord

GREEN = 0x00FF00
ORANGE = 0xFF6B35


def make_startup_embed(user: discord.abc.User) -> discord.Embed:
    e = discord.Embed(
        title="✅ Bot online",
        description="GameDealer is running and ready to post deals.",
        timestamp=datetime.now(timezone.utc),
        color=GREEN,
    )
    e.set_footer(text=f"Logged in as {user}")
    return e

def make_deal_embed(deal_data: dict) -> discord.Embed:
    title = deal_data.get("title", "Game Deal")
    price = deal_data.get("price", "Unknown")
    store = deal_data.get("store", "Unknown Store")
    url   = deal_data.get("url", "")

    embed = discord.Embed(
        title=f"🎮 {title}",
        description=f"**Price:** {price}\n**Store:** {store}",
        color=ORANGE,
        timestamp=datetime.now(timezone.utc),
    )
    if url:
        embed.add_field(name="Link", value=f"[Get Deal]({url})", inline=False)
        
    embed.set_footer(text="Powered by IsThereAnyDeal")
    return embed