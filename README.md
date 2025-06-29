# Discord AI Chatbot

A Discord bot powered by OpenRouter's DeepSeek model that provides real-time AI chat capabilities with conversation history and command support.

## Features

- 🤖 **AI-Powered Chat**: Uses DeepSeek model via OpenRouter API
- 💬 **Real-time Conversations**: Responds to messages with context awareness
- 📝 **Chat History**: Maintains conversation context during bot session
- ⚡ **Command Support**: Prefix-based commands for different interaction modes
- 🔄 **Rate Limiting**: Intelligent handling of API rate limits with exponential backoff
- 🎯 **Typing Indicators**: Shows when bot is generating responses
- 📊 **Statistics**: Track conversation metrics
- 🛡️ **Error Handling**: Robust error handling and logging
- 📦 **mongoDB support**: It comes with mongoDB support.

## Commands

- `!ask <question>` - Ask a direct question without conversation history
- `!chat <message>` - Chat with conversation history
- `!clear` - Clear conversation history for current channel/user
- `!stats` - Show chat statistics
- `!help` - Display help information

## Setup Instructions

### Prerequisites

1. **Discord Bot Token**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application and bot
   - Copy the bot token
   - Enable "Message Content Intent" in Bot settings

2. **OpenRouter API Key**:
   - Sign up at [OpenRouter](https://openrouter.ai/)
   - Get your API key from the dashboard
   - The bot uses the free `deepseek/deepseek-r1-0528-qwen3-8b:free` model

