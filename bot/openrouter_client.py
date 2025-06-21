"""
OpenRouter API client for AI chat functionality
"""

import asyncio
import json
import logging
import time
from typing import List, Dict, Any, Optional
import aiohttp
from bot.config import BotConfig

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Client for interacting with OpenRouter API"""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_times: List[float] = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def create_session(self):
        """Create HTTP session if not exists"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        current_time = time.time()
        
        # Remove old requests outside the window
        self.request_times = [
            req_time for req_time in self.request_times
            if current_time - req_time < self.config.rate_limit_window
        ]
        
        # Check if we can make another request
        return len(self.request_times) < self.config.rate_limit_requests
    
    def _record_request(self):
        """Record a new request timestamp"""
        self.request_times.append(time.time())
    
    async def _wait_for_rate_limit(self):
        """Wait until we can make another request"""
        if not self.request_times:
            return
        
        oldest_request = min(self.request_times)
        wait_time = self.config.rate_limit_window - (time.time() - oldest_request)
        
        if wait_time > 0:
            logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
            await asyncio.sleep(wait_time)
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        retry_count: int = 0
    ) -> Optional[str]:
        """
        Generate AI response using OpenRouter API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            retry_count: Current retry attempt
            
        Returns:
            Generated response string or None if failed
        """
        await self.create_session()
        
        # Check rate limits
        if not self._check_rate_limit():
            await self._wait_for_rate_limit()
        
        try:
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.config.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://discord-ai-bot",
                "X-Title": "Discord AI Bot"
            }
            
            # Add system prompt if not present
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {
                    "role": "system",
                    "content": self.config.system_prompt
                })
            
            payload = {
                "model": self.config.model_name,
                "messages": messages,
                "max_tokens": self.config.max_response_length,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": False
            }
            
            self._record_request()
            
            async with self.session.post(
                f"{self.config.openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if "choices" in data and data["choices"]:
                        content = data["choices"][0]["message"]["content"]
                        logger.info("Successfully generated AI response")
                        return content.strip()
                    else:
                        logger.error("No choices in API response")
                        return None
                
                elif response.status == 429:
                    # Rate limited
                    logger.warning(f"Rate limited by OpenRouter (429), retry {retry_count + 1}")
                    
                    if retry_count < self.config.max_retries:
                        delay = self.config.retry_delay_base * (2 ** retry_count)
                        await asyncio.sleep(delay)
                        return await self.generate_response(messages, retry_count + 1)
                    else:
                        logger.error("Max retries exceeded for rate limiting")
                        return "Sorry, I'm currently rate limited. Please try again later."
                
                else:
                    error_text = await response.text()
                    logger.error(f"OpenRouter API error {response.status}: {error_text}")
                    
                    if retry_count < self.config.max_retries:
                        delay = self.config.retry_delay_base * (2 ** retry_count)
                        await asyncio.sleep(delay)
                        return await self.generate_response(messages, retry_count + 1)
                    else:
                        return f"Sorry, I encountered an error: {response.status}"
        
        except asyncio.TimeoutError:
            logger.error("Request to OpenRouter API timed out")
            if retry_count < self.config.max_retries:
                return await self.generate_response(messages, retry_count + 1)
            return "Sorry, the request timed out. Please try again."
        
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            if retry_count < self.config.max_retries:
                return await self.generate_response(messages, retry_count + 1)
            return f"Sorry, I encountered an unexpected error: {str(e)}"
