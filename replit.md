# Discord AI Chatbot

## Overview

This is a Discord bot that provides real-time AI chat capabilities powered by OpenRouter's DeepSeek model. The bot maintains conversation history, supports various commands, and implements intelligent rate limiting with robust error handling.

## System Architecture

### Core Components
- **Discord Bot Client**: Built using discord.py library with command support
- **AI Integration**: OpenRouter API client using DeepSeek model (free tier)
- **Chat Management**: In-memory conversation history tracking
- **Configuration**: Environment-based configuration management
- **Rate Limiting**: Exponential backoff and request throttling

### Architecture Pattern
The application follows a modular architecture with separation of concerns:
- Bot logic separated from AI client
- Configuration management centralized
- Chat history managed independently
- Async/await pattern throughout for performance

## Key Components

### Discord Client (`bot/discord_client.py`)
- Main bot class extending `commands.Bot`
- Handles Discord events and message processing
- Integrates with chat manager and OpenRouter client
- Supports both command-based and natural conversation modes

### OpenRouter Client (`bot/openrouter_client.py`)
- HTTP client for OpenRouter API integration
- Implements rate limiting and retry logic
- Uses aiohttp for async HTTP requests
- Handles API authentication and error responses

### Chat Manager (`bot/chat_manager.py`)
- Manages conversation history per channel/user
- Implements message deques with configurable max length
- Supports both channel-based and user-based history tracking
- In-memory storage (no persistence across restarts)

### Configuration (`bot/config.py`)
- Environment variable-based configuration
- Validates required settings on startup
- Provides defaults for optional settings
- Handles type conversion and validation

## Data Flow

1. **Message Reception**: Discord client receives messages
2. **Command Processing**: Bot determines if message is a command or chat
3. **History Retrieval**: Chat manager provides conversation context
4. **AI Request**: OpenRouter client sends request with history
5. **Response Processing**: AI response is formatted and sent back
6. **History Update**: Both user message and AI response stored

## External Dependencies

### Required APIs
- **Discord Bot API**: Requires bot token and Message Content Intent
- **OpenRouter API**: Uses free DeepSeek model (`deepseek/deepseek-r1-0528-qwen3-8b:free`)

### Python Packages
- `discord.py>=2.5.2`: Discord bot framework
- `aiohttp>=3.12.13`: Async HTTP client
- `python-dotenv>=1.1.0`: Environment variable management

### Environment Variables
- `DISCORD_TOKEN`: Discord bot authentication token
- `OPENROUTER_API_KEY`: OpenRouter API authentication
- `COMMAND_PREFIX`: Bot command prefix (default: "!")
- `CHAT_CHANNEL_ID`: Optional specific channel ID for chat
- Various behavior and rate limiting settings

## Deployment Strategy

### Replit Deployment
- Configured for Python 3.11 environment
- Uses Nix package manager for dependencies
- Automatic dependency installation on startup
- Workflow-based execution model

### Local Development
- Environment file-based configuration
- Pip-based dependency management
- File-based logging support
- Hot reload capabilities during development

### Production Considerations
- No database persistence (chat history lost on restart)
- Rate limiting configured for free tier usage
- Error logging to both console and file
- Graceful shutdown handling

## Recent Changes

- June 21, 2025: Enhanced Discord AI chatbot with advanced features
  - Added comprehensive fun commands: joke, game (trivia/math/word/riddle), guess, roll, flip
  - Implemented admin command system with channel management and prefix control
  - Set user ID 782306059469193257 as bot administrator
  - Added support server integration (https://discord.gg/k7Sss4yKj5)
  - Enhanced help system with categorized command display
  - Added auto-reaction feature for improved user engagement
  - Bot successfully restarted with all new features functional

## Changelog

```
Changelog:
- June 21, 2025: Initial setup and full implementation
- June 21, 2025: Bot successfully deployed and tested
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```