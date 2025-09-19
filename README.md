# GameDealer Discord Bot

A well-structured Discord bot built with Python and discord.py, featuring modular architecture and best practices.

## 🏗️ Project Structure

```
GameDealer/
├── main.py                 # Entry point - initializes and runs the bot
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create this file)
├── bot/                   # Core bot functionality
│   ├── __init__.py
│   └── core.py           # Main bot class and setup
├── cogs/                  # Command and event modules
│   ├── general.py        # General commands (hello, ping, info)
│   ├── member_events.py  # Member join/leave events
│   └── moderation.py     # Message filtering and moderation
├── config/                # Configuration management
│   ├── __init__.py
│   └── settings.py       # Bot configuration and environment variables
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── message_utils.py  # Message processing helpers
│   └── logging_utils.py  # Logging utilities
└── logs/                  # Log files (auto-created)
    └── discord.log
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd GameDealer
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
DISCORD_TOKEN=your_bot_token_here
COMMAND_PREFIX=!
LOG_LEVEL=INFO
WELCOME_NEW_MEMBERS=true
```

### 3. Run the Bot

```bash
python main.py
```

## 📁 Understanding the Structure

### **main.py** - Entry Point

-   Clean entry point that initializes the bot
-   Handles startup, configuration validation, and error handling
-   No bot logic here - just initialization!

### **bot/core.py** - Bot Class

-   Contains the main `GameDealerBot` class
-   Handles cog loading, error handling, and bot events
-   Extensible and maintainable bot foundation

### **cogs/** - Modular Commands

-   **general.py**: Basic commands (hello, ping, info)
-   **member_events.py**: Member join/leave handling
-   **moderation.py**: Message filtering and moderation tools

### **config/settings.py** - Configuration

-   Centralized configuration management
-   Environment variable handling
-   Logging setup

### **utils/** - Reusable Functions

-   **message_utils.py**: Message processing, embed creation
-   **logging_utils.py**: Enhanced logging functionality

## 🔧 Key Features

### Modular Design

-   **Cogs**: Commands and events are separated into logical modules
-   **Easy Extension**: Add new features by creating new cog files
-   **Hot Reloading**: Load/unload cogs without restarting the bot

### Configuration Management

-   Environment variables for sensitive data
-   Centralized settings in `config/settings.py`
-   Easy to modify bot behavior without code changes

### Error Handling

-   Global error handling for commands
-   Graceful degradation and user-friendly error messages
-   Comprehensive logging for debugging

### Utility Functions

-   Reusable message processing functions
-   Consistent embed styling
-   Modular logging system

## 🎯 Best Practices Demonstrated

### 1. **Separation of Concerns**

```python
# ❌ Bad: Everything in main.py
@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")

# ✅ Good: Commands in separate cogs
class GeneralCommands(commands.Cog):
    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Hello!")
```

### 2. **Configuration Management**

```python
# ❌ Bad: Hardcoded values
bot = commands.Bot(command_prefix='!')

# ✅ Good: Configurable settings
bot = commands.Bot(command_prefix=BotConfig.COMMAND_PREFIX)
```

### 3. **Error Handling**

```python
# ❌ Bad: No error handling
await ctx.send(f"Hello {user.name}")

# ✅ Good: Proper error handling
try:
    await ctx.send(f"Hello {user.name}")
except discord.Forbidden:
    await ctx.send("I don't have permission to send messages!")
```

### 4. **Reusable Functions**

```python
# ❌ Bad: Duplicate code
embed1 = discord.Embed(title="Error", color=discord.Color.red())
embed2 = discord.Embed(title="Another Error", color=discord.Color.red())

# ✅ Good: Utility functions
embed1 = create_error_embed("Error", "Something went wrong")
embed2 = create_error_embed("Another Error", "Something else went wrong")
```

## 🛠️ Adding New Features

### Adding a New Command

1. Choose the appropriate cog file (or create a new one)
2. Add your command to the cog class
3. The bot will automatically load it on startup

```python
# In cogs/general.py
@commands.command(name='mycmd', help='My new command')
async def my_command(self, ctx):
    await ctx.send("This is my new command!")
```

### Adding a New Cog

1. Create a new file in the `cogs/` directory
2. Follow the cog structure pattern
3. Include the `setup()` function

```python
# cogs/newfeature.py
from discord.ext import commands

class NewFeature(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def newcmd(self, ctx):
        await ctx.send("New feature!")

async def setup(bot):
    await bot.add_cog(NewFeature(bot))
```

### Adding Utility Functions

1. Add functions to appropriate files in `utils/`
2. Update `utils/__init__.py` to export them
3. Import and use in your cogs

## 🔍 Environment Variables

| Variable              | Description               | Default            |
| --------------------- | ------------------------- | ------------------ |
| `DISCORD_TOKEN`       | Your bot token (required) | None               |
| `COMMAND_PREFIX`      | Bot command prefix        | `!`                |
| `LOG_LEVEL`           | Logging level             | `INFO`             |
| `LOG_FILE`            | Log file path             | `logs/discord.log` |
| `WELCOME_NEW_MEMBERS` | Send welcome messages     | `true`             |

## 📚 Learning Resources

-   [Discord.py Documentation](https://discordpy.readthedocs.io/)
-   [Discord Developer Portal](https://discord.com/developers/applications)
-   [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

## 🤝 Contributing

1. Follow the existing code structure
2. Add appropriate error handling
3. Update documentation for new features
4. Test your changes thoroughly

## 📝 License

This project is open source and available under the [MIT License](LICENSE).
