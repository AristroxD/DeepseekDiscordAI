#!/usr/bin/env python3
"""
Discord AI Chatbot - Main Entry Point
Connects to Discord and OpenRouter for real-time AI conversations
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from bot.discord_client import DiscordBot
from bot.config import BotConfig

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to start the Discord bot"""
    try:
        # Initialize configuration
        config = BotConfig()
        
        # Validate required environment variables
        if not config.discord_token:
            logger.error("DISCORD_TOKEN environment variable is required")
            return
        
        if not config.openrouter_api_key:
            logger.error("OPENROUTER_API_KEY environment variable is required")
            return
        
        logger.info("Starting Discord AI Chatbot...")
        
        # Initialize and start the bot
        bot = DiscordBot(config)
        await bot.start(config.discord_token)
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        logger.info("Bot shutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
