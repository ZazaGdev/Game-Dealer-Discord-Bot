# utils/embeds.py
import discord
from datetime import datetime, timezone
from typing import Union, Optional
from models import Deal

GREEN: int = 0x00FF00
ORANGE: int = 0xFF6B35
RED: int = 0xE74C3C
BLUE: int = 0x3498DB

def make_startup_embed(user: Union[discord.User, discord.Member, discord.abc.User]) -> discord.Embed:
    """Create a startup embed with proper type safety"""
    e = discord.Embed(
        title="✅ Bot online",
        description="GameDealer is running and ready to post deals.",
        timestamp=datetime.now(timezone.utc),
        color=GREEN,
    )
    e.set_footer(text=f"Logged in as {user}")
    return e

def make_deal_embed(deal_data: Deal) -> discord.Embed:
    """Create a deal embed with type safety and validation"""
    title: str = deal_data.get("title", "Game Deal")
    price: str = deal_data.get("price", "Unknown")
    store: str = deal_data.get("store", "Unknown Store")
    url: str = deal_data.get("url", "")
    discount: Optional[str] = deal_data.get("discount")
    original_price: Optional[str] = deal_data.get("original_price")

    # Choose color based on discount percentage
    color: int = ORANGE  # default
    if discount:
        try:
            discount_num = int(discount.replace('%', ''))
            if discount_num >= 80:
                color = RED  # Amazing deal
            elif discount_num >= 60:
                color = GREEN  # Great deal
            else:
                color = BLUE  # Good deal
        except (ValueError, AttributeError):
            pass

    embed = discord.Embed(
        title=f"🎮 {title}",
        color=color,
        timestamp=datetime.now(timezone.utc),
    )
    
    # Enhanced price display
    price_field = f"**Current Price:** {price}"
    if original_price and discount:
        price_field += f"\n**Original Price:** ~~{original_price}~~"
        price_field += f"\n**Discount:** {discount} OFF!"
    
    embed.add_field(name="💰 Price", value=price_field, inline=True)
    embed.add_field(name="🏪 Store", value=store, inline=True)
    
    if url:
        embed.add_field(name="🔗 Link", value=f"[Get This Deal]({url})", inline=False)
    
    # Add discount indicator in footer
    footer_text = "Powered by IsThereAnyDeal"
    if discount:
        try:
            discount_num = int(discount.replace('%', ''))
            if discount_num >= 80:
                footer_text = "🔥 MEGA DEAL! • " + footer_text
            elif discount_num >= 60:
                footer_text = "⭐ GREAT DEAL! • " + footer_text
        except (ValueError, AttributeError):
            pass
    
    embed.set_footer(text=footer_text)
    return embed