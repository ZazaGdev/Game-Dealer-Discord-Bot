# 🎮 GameDealer Discord Bot

**Find the best game deals across Steam, Epic Games Store, GOG, and 20+ other stores with intelligent filtering and a curated database of quality games.**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0+-green.svg)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ Features

-   🎯 **Curated Game Database**: 1,173+ quality games with priority ratings (1-10)
-   🔍 **Smart Search**: Exact title matching prevents false positives
-   🏪 **Multi-Store Support**: Steam, Epic, GOG, and 20+ other stores
-   📊 **Advanced Filtering**: By priority level, discount percentage, and store
-   ⚡ **Automated Updates**: Fresh deals fetched daily at 9 AM
-   🚀 **Type-Safe**: Comprehensive type annotations throughout codebase

## 🚀 Quick Start

### For Users (Adding to Discord Server)

1. **Invite Bot**: [Click here to invite GameDealer](https://discord.com/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=274877908032&scope=bot%20applications.commands) _(Replace YOUR_BOT_ID)_
2. **Use Commands**: Start with `/priority_search` for curated game deals
3. **Get Help**: Use `/help` to see all available commands

### For Developers (Self-Hosting)

```bash
# Clone repository
git clone https://github.com/ZazaGdev/GameDealer.git
cd GameDealer

# Install dependencies
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your tokens

# Run bot
python main.py
```

## 🎮 Commands

| Command            | Description                     | Example                                           |
| ------------------ | ------------------------------- | ------------------------------------------------- |
| `/priority_search` | Find curated quality game deals | `/priority_search min_priority:8 min_discount:50` |
| `/search_deals`    | Browse all available deals      | `/search_deals amount:15`                         |
| `/search_store`    | Deals from specific store       | `/search_store store:Steam amount:10`             |
| `/help`            | Show all commands               | `/help`                                           |
| `/info`            | Bot statistics and health       | `/info`                                           |
| `/ping`            | Check bot latency               | `/ping`                                           |

## 📊 Priority Rating System

Our curated database rates games on a 1-10 scale based on quality, reviews, and popularity:

| Rating  | Category         | Examples                               |
| ------- | ---------------- | -------------------------------------- |
| **10**  | Game of the Year | The Witcher 3, Elden Ring, Hades       |
| **9**   | Exceptional AAA  | Cyberpunk 2077, Red Dead Redemption 2  |
| **8**   | Great Games      | Hollow Knight, Divinity Original Sin 2 |
| **7**   | Solid Titles     | Assassin's Creed series, Rocket League |
| **6-5** | Good Games       | Stardew Valley, Among Us               |
| **4-1** | Niche/Casual     | Various indie and specialized games    |

## 🛠️ Setup & Configuration

### Prerequisites

-   Python 3.11+
-   Discord Bot Token ([Create one here](https://discord.com/developers/applications))
-   ITAD API Key ([Get free key](https://isthereanydeal.com/apps/my/))

### Environment Variables

Create a `.env` file:

```env
DISCORD_TOKEN=your_discord_bot_token_here
ITAD_API_KEY=your_itad_api_key_here
LOG_CHANNEL_ID=123456789  # Optional: Discord channel for logs
DEALS_CHANNEL_ID=987654321  # Optional: Channel for automated deals
```

### Discord Bot Permissions

Required permissions for full functionality:

-   Send Messages
-   Use Slash Commands
-   Embed Links
-   Add Reactions
-   Read Message History

## 📁 Project Structure

```
GameDealer/
├── main.py                    # Bot entry point
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables (create this)
├── .gitignore               # Git ignore rules
│
├── api/                     # External API integration
│   ├── http.py             # HTTP client with retry logic
│   └── itad_client.py      # ITAD API wrapper
│
├── bot/                     # Discord bot core
│   ├── core.py            # Bot initialization & command sync
│   └── scheduler.py       # Automated task scheduling
│
├── cogs/                    # Command modules
│   ├── deals.py          # Deal search commands
│   └── general.py        # Utility commands (help, info, ping)
│
├── config/                  # Configuration management
│   ├── app_config.py      # Environment loading & validation
│   └── logging_config.py  # Logging configuration
│
├── data/                    # Game database
│   └── priority_games.json # 1,173+ curated games database
│
├── models/                  # Type definitions
│   └── models.py          # TypedDict & Protocol definitions
│
├── utils/                   # Utility functions
│   ├── embeds.py         # Discord embed helpers
│   ├── game_filters.py   # Game matching & filtering logic
│   └── api_health.py     # API status monitoring
│
├── docs/                    # Documentation
│   ├── README.md         # User guide & command reference
│   ├── SETUP.md          # Detailed setup instructions
│   ├── TECHNICAL_DOCUMENTATION.md # Architecture & API docs
│   └── api_templates.md  # API response examples
│
├── tests/                   # Test suite
└── logs/                    # Runtime logs
```

## 🔧 Development

### Running Tests

```bash
# Test API connectivity
python tests/debug_api.py

# Test priority search functionality
python tests/test_priority_search.py

# Check API health status
python utils/api_health.py
```

### Adding Games to Database

Edit `data/priority_games.json`:

```json
{
    "title": "Game Name",
    "priority": 8,
    "category": "RPG",
    "notes": "Optional description"
}
```

### Code Quality

This project uses comprehensive type annotations:

-   TypedDict for structured data
-   Protocol interfaces for duck typing
-   Union types for flexible parameters
-   Optional types for nullable values

## 🚀 Deployment

### Production Environment

```env
DEBUG=false
LOG_LEVEL=INFO
API_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=10
```

### Monitoring

-   Monitor `logs/discord.log` for errors and performance
-   Use `/ping` and `/info` commands for health checks
-   Set up automated API health monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes with proper type annotations
4. Test thoroughly
5. Submit a pull request

### Code Style

-   Use type hints throughout
-   Follow PEP 8 conventions
-   Add docstrings for public functions
-   Keep functions focused and testable

## 📋 Supported Stores

**Primary Stores** (prioritized):

-   Steam
-   Epic Games Store
-   GOG (Good Old Games)

**Additional Stores**:
Humble Bundle, Green Man Gaming, Fanatical, GamesPlanet, Microsoft Store, PlayStation Store, and 15+ others.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

-   **Documentation**: Check [docs/README.md](docs/README.md) for detailed user guide
-   **Setup Issues**: See [docs/SETUP.md](docs/SETUP.md) for troubleshooting
-   **Technical Details**: Review [docs/TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md)
-   **Issues**: Open an issue on GitHub
-   **Discord**: Use `/help` command for bot assistance

## 🏆 Acknowledgments

-   [IsThereAnyDeal.com](https://isthereanydeal.com) for providing the deal data API
-   [Discord.py](https://discordpy.readthedocs.io/) for the excellent Discord library
-   Game database curated from community recommendations and review aggregates

---

**Made with ❤️ for the gaming community**
