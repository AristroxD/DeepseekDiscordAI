"""
Configuration management for the Discord AI bot
"""

import os
from typing import Optional

class BotConfig:
    """Configuration class for bot settings"""
    
    def __init__(self):
        # Discord settings
        self.discord_token: str = os.getenv("DISCORD_TOKEN", "")
        self.command_prefix: str = os.getenv("COMMAND_PREFIX", "!")
        self.chat_channel_id: Optional[int] = self._get_channel_id()
        
        # OpenRouter settings
        self.openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
        self.openrouter_base_url: str = "https://openrouter.ai/api/v1"
        self.model_name: str = "deepseek/deepseek-r1-0528-qwen3-8b:free"
        
        # Bot personality and behavior
        self.system_prompt: str = self._get_system_prompt()
        self.max_history_messages: int = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
        self.max_response_length: int = int(os.getenv("MAX_RESPONSE_LENGTH", "2000"))
        
        # Rate limiting settings
        self.rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
        self.rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        self.retry_delay_base: float = float(os.getenv("RETRY_DELAY_BASE", "1.0"))
        self.max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
        
    def _get_channel_id(self) -> Optional[int]:
        """Get chat channel ID from environment"""
        channel_id = os.getenv("CHAT_CHANNEL_ID")
        if channel_id:
            try:
                return int(channel_id)
            except ValueError:
                return None
        return None
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the AI"""
        default_prompt = """You are a friendly and helpful AI assistant on Discord. 
        You should be conversational, engaging, and provide useful responses. 
        Keep your messages concise but informative. Use Discord markdown when appropriate 
        (like **bold** for emphasis, `code` for code snippets, etc.). 
        Be respectful and maintain a positive tone in all interactions."""
        
        return os.getenv("SYSTEM_PROMPT", default_prompt)
    
    def validate(self) -> bool:
        """Validate that required configuration is present"""
        required_vars = [
            ("DISCORD_TOKEN", self.discord_token),
            ("OPENROUTER_API_KEY", self.openrouter_api_key)
        ]
        
        for var_name, var_value in required_vars:
            if not var_value:
                print(f"Error: {var_name} environment variable is required")
                return False
        
        return True
