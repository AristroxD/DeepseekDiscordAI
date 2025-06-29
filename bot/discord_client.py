"""
Discord bot client with AI chat integration
"""

import logging
import asyncio
import random
from typing import Optional
import discord
from discord.ext import commands

from bot.config import BotConfig
from bot.openrouter_client import OpenRouterClient
from bot.chat_manager import ChatManager

logger = logging.getLogger(__name__)

class DiscordBot(commands.Bot):
    """Discord bot with AI chat capabilities"""
    
    def __init__(self, config: BotConfig):
        # Configure intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True

        
        super().__init__(
            command_prefix=config.command_prefix,
            intents=intents,
            help_command=None
        )
        
        self.config = config
        self.chat_manager = ChatManager(config.max_history_messages)
        self.openrouter_client: Optional[OpenRouterClient] = None
    
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        logger.info("Setting up Discord bot...")
        
        # Load chat channel from MongoDB if available
        from bot.db import get_collection
        channels = get_collection("channels")
        if self.guilds:
            for guild in self.guilds:
                doc = channels.find_one({"guild_id": guild.id})
                if doc:
                    self.config.chat_channel_id = doc["channel_id"]
                    logger.info(f"Loaded chat channel {doc['channel_id']} for guild {guild.id}")
        
        # Initialize OpenRouter client
        self.openrouter_client = OpenRouterClient(self.config)
        await self.openrouter_client.create_session()
        
        # Add commands
        await self.add_cog(ChatCommands(self))
        
        # Import and add new command cogs
        from bot.fun_commands import FunCommands
        from bot.admin_commands import AdminCommands
        await self.add_cog(FunCommands(self))
        await self.add_cog(AdminCommands(self))
        
        logger.info("Discord bot setup complete")
    
    async def close(self):
        """Clean shutdown"""
        if self.openrouter_client:
            await self.openrouter_client.close_session()
        await super().close()
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{self.config.command_prefix}help | AI Chat Bot"
        )
        await self.change_presence(activity=activity)
        
        # Log configuration
        if self.config.chat_channel_id:
            logger.info(f"Configured for chat channel ID: {self.config.chat_channel_id}")
        else:
            logger.info("No specific chat channel configured - will respond in DMs and mentions")
    
    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        # Ignore messages from bots (including self)
        if message.author.bot:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Skip if it was a command
        if message.content.startswith(self.config.command_prefix):
            return
        
        # Check if we should respond to this message
        should_respond = await self._should_respond_to_message(message)
        
        if should_respond:
            await self._handle_chat_message(message)
    
    async def _should_respond_to_message(self, message: discord.Message) -> bool:
        """Determine if bot should respond to a message"""
        # Always respond to DMs
        if isinstance(message.channel, discord.DMChannel):
            return True
        
        # If specific channel is configured, only respond there
        if self.config.chat_channel_id:
            return message.channel.id == self.config.chat_channel_id
        
        # Otherwise, respond to mentions
        return self.user in message.mentions
    
    async def _handle_chat_message(self, message: discord.Message):
        """Handle chat message and generate AI response"""
        try:
            # Show typing indicator
            async with message.channel.typing():
                # Add auto-reactions if enabled
                if self.config.enable_auto_reactions and random.random() < 0.1:  # 10% chance
                    reactions = ["👍", "😊", "🤔", "💡", "❤️", "🎉"]
                    try:
                        await message.add_reaction(random.choice(reactions))
                    except:
                        pass  # Ignore reaction errors
                
                # Add user message to history
                self.chat_manager.add_message(
                    channel_id=message.channel.id,
                    user_id=message.author.id,
                    content=message.content,
                    role="user"
                )
                
                # Get conversation context
                if isinstance(message.channel, discord.DMChannel):
                    context = self.chat_manager.get_conversation_context(user_id=message.author.id)
                else:
                    context = self.chat_manager.get_conversation_context(channel_id=message.channel.id)
                
                # Generate AI response
                response = await self.openrouter_client.generate_response(context)
                
                if response:
                    # Split long responses if needed
                    if len(response) > 2000:
                        chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                        for chunk in chunks:
                            await message.channel.send(chunk)
                    else:
                        await message.channel.send(response)
                    
                    # Add bot response to history
                    self.chat_manager.add_message(
                        channel_id=message.channel.id,
                        user_id=self.user.id,
                        content=response,
                        role="assistant"
                    )
                    
                    logger.info(f"Responded to message from {message.author} in {message.channel}")
                else:
                    await message.channel.send("Sorry, I couldn't generate a response right now. Please try again.")
        
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await message.channel.send("Sorry, I encountered an error while processing your message.")
    
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        logger.error(f"Command error in {ctx.command}: {error}")
        await ctx.send(f"An error occurred: {str(error)}")

class ChatCommands(commands.Cog):
    """Chat-related commands"""
    
    def __init__(self, bot: DiscordBot):
        self.bot = bot
    
    @commands.command(name="ask")
    async def ask_command(self, ctx: commands.Context, *, question: str):
        """Ask the AI a question directly"""
        async with ctx.typing():
            try:
                # Create a one-off conversation with the question
                messages = [
                    {"role": "system", "content": self.bot.config.system_prompt},
                    {"role": "user", "content": question}
                ]
                
                response = await self.bot.openrouter_client.generate_response(messages)
                
                if response:
                    if len(response) > 2000:
                        chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                        for chunk in chunks:
                            await ctx.send(chunk)
                    else:
                        await ctx.send(response)
                else:
                    await ctx.send("Sorry, I couldn't generate a response to your question.")
            
            except Exception as e:
                logger.error(f"Error in ask command: {e}")
                await ctx.send("Sorry, I encountered an error while processing your question.")
    
    @commands.command(name="chat")
    async def chat_command(self, ctx: commands.Context, *, message: str):
        """Chat with the AI (includes conversation history)"""
        async with ctx.typing():
            try:
                # Add user message to history
                self.bot.chat_manager.add_message(
                    channel_id=ctx.channel.id,
                    user_id=ctx.author.id,
                    content=message,
                    role="user"
                )
                
                # Get conversation context
                if isinstance(ctx.channel, discord.DMChannel):
                    context = self.bot.chat_manager.get_conversation_context(user_id=ctx.author.id)
                else:
                    context = self.bot.chat_manager.get_conversation_context(channel_id=ctx.channel.id)
                
                response = await self.bot.openrouter_client.generate_response(context)
                
                if response:
                    if len(response) > 2000:
                        chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                        for chunk in chunks:
                            await ctx.send(chunk)
                    else:
                        await ctx.send(response)
                    
                    # Add bot response to history
                    self.bot.chat_manager.add_message(
                        channel_id=ctx.channel.id,
                        user_id=self.bot.user.id,
                        content=response,
                        role="assistant"
                    )
                else:
                    await ctx.send("Sorry, I couldn't generate a response.")
            
            except Exception as e:
                logger.error(f"Error in chat command: {e}")
                await ctx.send("Sorry, I encountered an error while processing your message.")
    
    @commands.command(name="clear")
    async def clear_history(self, ctx: commands.Context):
        """Clear chat history for this channel/user"""
        try:
            if isinstance(ctx.channel, discord.DMChannel):
                self.bot.chat_manager.clear_history(user_id=ctx.author.id)
            else:
                self.bot.chat_manager.clear_history(channel_id=ctx.channel.id)
            
            await ctx.send("✅ Chat history cleared!")
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            await ctx.send("❌ Error clearing chat history.")
    
    @commands.command(name="stats")
    async def chat_stats(self, ctx: commands.Context):
        """Show chat statistics"""
        try:
            stats = self.bot.chat_manager.get_stats()
            
            embed = discord.Embed(
                title="📊 Chat Statistics",
                color=discord.Color.blue()
            )
            embed.add_field(name="Total Channels", value=stats["total_channels"], inline=True)
            embed.add_field(name="Total Users", value=stats["total_users"], inline=True)
            embed.add_field(name="Channel Messages", value=stats["total_channel_messages"], inline=True)
            embed.add_field(name="User Messages", value=stats["total_user_messages"], inline=True)
            embed.add_field(name="Max History", value=stats["max_history_per_conversation"], inline=True)
            
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            await ctx.send("❌ Error retrieving statistics.")
    
    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context, category: str = None):
        """Show help information"""
        if category == "fun":
            embed = discord.Embed(
                title="🎮 Fun Commands",
                description="Entertainment and games!",
                color=discord.Color.gold()
            )
            embed.add_field(name=f"{self.bot.config.command_prefix}joke", value="Tell a random joke", inline=True)
            embed.add_field(name=f"{self.bot.config.command_prefix}fun", value="Random fun activities", inline=True)
            embed.add_field(name=f"{self.bot.config.command_prefix}roll [sides]", value="Roll a dice", inline=True)
            embed.add_field(name=f"{self.bot.config.command_prefix}flip", value="Flip a coin", inline=True)
            embed.add_field(name=f"{self.bot.config.command_prefix}guess [max]", value="Number guessing game", inline=True)
            embed.add_field(name=f"{self.bot.config.command_prefix}game <type>", value="Start mini-games (trivia, math, word, riddle)", inline=False)
            
        elif category == "admin" and ctx.author.id == self.bot.config.admin_user_id:
            embed = discord.Embed(
                title="⚙️ Admin Commands",
                description="Bot management commands (Admin only)",
                color=discord.Color.red()
            )
            embed.add_field(name=f"{self.bot.config.command_prefix}setchannel [#channel]", value="Set main chat channel", inline=True)
            embed.add_field(name=f"{self.bot.config.command_prefix}unsetchannel", value="Remove channel restriction", inline=True)
            embed.add_field(name=f"{self.bot.config.command_prefix}setprefix <prefix>", value="Change command prefix", inline=True)
            embed.add_field(name=f"{self.bot.config.command_prefix}botstats", value="Detailed bot statistics", inline=True)
            embed.add_field(name=f"{self.bot.config.command_prefix}clearall", value="Clear all chat history", inline=True)
            embed.add_field(name=f"{self.bot.config.command_prefix}say [#channel] <message>", value="Make bot say something", inline=True)
            embed.add_field(name=f"{self.bot.config.command_prefix}shutdown", value="Shutdown bot", inline=True)
            embed.add_field(name=f"{self.bot.config.command_prefix}eval <code>", value="Execute Python code", inline=True)
            
        else:
            embed = discord.Embed(
                title="🤖 AI Chat Bot Help",
                description="I'm an AI assistant powered by DeepSeek. Here's how to interact with me:",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="💬 Chat Commands",
                value=f"`{self.bot.config.command_prefix}ask <question>` - Direct question\n"
                      f"`{self.bot.config.command_prefix}chat <message>` - Chat with history\n"
                      f"`{self.bot.config.command_prefix}clear` - Clear history\n"
                      f"`{self.bot.config.command_prefix}stats` - Chat statistics",
                inline=False
            )
            
            embed.add_field(
                name="🎮 Fun & Games",
                value=f"`{self.bot.config.command_prefix}help fun` - See all fun commands\n"
                      f"`{self.bot.config.command_prefix}joke` - Random joke\n"
                      f"`{self.bot.config.command_prefix}game trivia` - Play trivia\n"
                      f"`{self.bot.config.command_prefix}guess` - Number guessing",
                inline=False
            )
            
            embed.add_field(
                name="ℹ️ Other Commands",
                value=f"`{self.bot.config.command_prefix}invite` - Get bot invite link\n"
                      f"**Natural Chat:** Just mention me or send a DM!",
                inline=False
            )
            
            if ctx.author.id == self.bot.config.admin_user_id:
                embed.add_field(
                    name="⚙️ Admin",
                    value=f"`{self.bot.config.command_prefix}help admin` - Admin commands",
                    inline=False
                )
        
        embed.set_footer(text=f"Powered by OpenRouter & DeepSeek | Support: {self.bot.config.help_server_invite}")
        await ctx.send(embed=embed)
