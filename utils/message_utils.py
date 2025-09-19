"""
Message utility functions for the Discord bot.
This module contains helper functions for message processing, filtering, and formatting.
"""

import discord
from typing import List

def should_filter_message(content: str, filtered_words: List[str]) -> bool:
    """
    Check if a message contains any filtered words.
    
    Args:
        content (str): The message content to check
        filtered_words (List[str]): List of words to filter
    
    Returns:
        bool: True if the message should be filtered, False otherwise
    """
    if not content or not filtered_words:
        return False
    
    content_lower = content.lower()
    
    for word in filtered_words:
        if word.lower() in content_lower:
            return True
    
    return False

def create_warning_embed(user: discord.User, reason: str) -> discord.Embed:
    """
    Create a warning embed for moderation actions.
    
    Args:
        user (discord.User): The user being warned
        reason (str): The reason for the warning
    
    Returns:
        discord.Embed: The formatted warning embed
    """
    embed = discord.Embed(
        title="⚠️ Warning",
        description=f"{user.mention}, {reason}",
        color=discord.Color.orange()
    )
    embed.set_footer(text="Please follow the server rules.")
    return embed

def create_success_embed(title: str, description: str) -> discord.Embed:
    """
    Create a success embed with consistent styling.
    
    Args:
        title (str): The embed title
        description (str): The embed description
    
    Returns:
        discord.Embed: The formatted success embed
    """
    embed = discord.Embed(
        title=f"✅ {title}",
        description=description,
        color=discord.Color.green()
    )
    return embed

def create_error_embed(title: str, description: str) -> discord.Embed:
    """
    Create an error embed with consistent styling.
    
    Args:
        title (str): The embed title
        description (str): The embed description
    
    Returns:
        discord.Embed: The formatted error embed
    """
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=discord.Color.red()
    )
    return embed

def truncate_text(text: str, max_length: int = 2000) -> str:
    """
    Truncate text to fit Discord's character limits.
    
    Args:
        text (str): The text to truncate
        max_length (int): Maximum length (default: 2000 for embed descriptions)
    
    Returns:
        str: The truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."