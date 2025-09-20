# config/logging_config.py
import logging
import os

# Write logs into ./logs/discord.log 
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  
LOG_DIR = os.path.join(ROOT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging(level=logging.INFO):
    if logging.getLogger().handlers:
        # Already configured 
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(LOG_DIR, "discord.log"), encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
