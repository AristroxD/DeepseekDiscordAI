"""
Chat history and context management
"""

import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class ChatManager:
    """Manages chat history and context for conversations"""
    
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        # Store chat history per channel/user
        self.channel_histories: Dict[int, deque] = defaultdict(
            lambda: deque(maxlen=self.max_history)
        )
        self.user_histories: Dict[int, deque] = defaultdict(
            lambda: deque(maxlen=self.max_history)
        )
    
    def add_message(
        self, 
        channel_id: int, 
        user_id: int, 
        content: str, 
        role: str = "user"
    ):
        """
        Add a message to chat history
        
        Args:
            channel_id: Discord channel ID
            user_id: Discord user ID
            content: Message content
            role: Message role (user, assistant, system)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": None,  # Could add timestamp if needed
            "user_id": user_id
        }
        
        # Add to channel history
        self.channel_histories[channel_id].append(message)
        
        # Add to user history for DMs
        if role == "user":
            self.user_histories[user_id].append(message)
        
        logger.debug(f"Added message to history - Channel: {channel_id}, User: {user_id}")
    
    def get_channel_history(self, channel_id: int) -> List[Dict[str, Any]]:
        """
        Get chat history for a specific channel
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            List of message dictionaries
        """
        return list(self.channel_histories[channel_id])
    
    def get_user_history(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get chat history for a specific user (for DMs)
        
        Args:
            user_id: Discord user ID
            
        Returns:
            List of message dictionaries
        """
        return list(self.user_histories[user_id])
    
    def get_conversation_context(
        self, 
        channel_id: Optional[int] = None, 
        user_id: Optional[int] = None,
        include_system: bool = True
    ) -> List[Dict[str, str]]:
        """
        Get conversation context for API calls
        
        Args:
            channel_id: Discord channel ID (for channel conversations)
            user_id: Discord user ID (for DM conversations)
            include_system: Whether to include system messages
            
        Returns:
            List of messages formatted for OpenRouter API
        """
        if channel_id:
            history = self.get_channel_history(channel_id)
        elif user_id:
            history = self.get_user_history(user_id)
        else:
            return []
        
        # Filter and format messages for API
        api_messages = []
        
        for message in history:
            # Skip system messages if not requested
            if not include_system and message["role"] == "system":
                continue
            
            # Format for API
            api_message = {
                "role": message["role"],
                "content": message["content"]
            }
            api_messages.append(api_message)
        
        return api_messages
    
    def clear_history(self, channel_id: Optional[int] = None, user_id: Optional[int] = None):
        """
        Clear chat history for a channel or user
        
        Args:
            channel_id: Discord channel ID to clear
            user_id: Discord user ID to clear
        """
        if channel_id and channel_id in self.channel_histories:
            self.channel_histories[channel_id].clear()
            logger.info(f"Cleared history for channel {channel_id}")
        
        if user_id and user_id in self.user_histories:
            self.user_histories[user_id].clear()
            logger.info(f"Cleared history for user {user_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about chat history
        
        Returns:
            Dictionary with statistics
        """
        total_channels = len(self.channel_histories)
        total_users = len(self.user_histories)
        total_messages = sum(len(history) for history in self.channel_histories.values())
        total_user_messages = sum(len(history) for history in self.user_histories.values())
        
        return {
            "total_channels": total_channels,
            "total_users": total_users,
            "total_channel_messages": total_messages,
            "total_user_messages": total_user_messages,
            "max_history_per_conversation": self.max_history
        }
