"""
Admin commands for Discord bot management
"""

import logging
import json
import discord
from discord.ext import commands
from typing import Optional
from bot.db import get_collection  # <-- Add this import

logger = logging.getLogger(__name__)

class AdminCommands(commands.Cog):
    """Admin-only commands for bot management"""
    
    def __init__(self, bot):
        self.bot = bot
        
    def is_admin(self, user_id: int) -> bool:
        """Check if user is the bot admin"""
        return user_id == self.bot.config.admin_user_id
    
    @commands.command(name="setchannel")
    async def set_chat_channel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Set the main chat channel for the bot (Admin only)"""
        if not self.is_admin(ctx.author.id):
            await ctx.send("Only the bot admin can use this command!")
            return
        
        if channel is None:
            channel = ctx.channel
        
        # Update the bot's chat channel
        self.bot.config.chat_channel_id = channel.id
        
        # Save to MongoDB for persistence
        channels = get_collection("channels")
        if ctx.guild:
            channels.update_one(
                {"guild_id": ctx.guild.id},
                {"$set": {"guild_id": ctx.guild.id, "channel_id": channel.id}},
                upsert=True
            )
        
        embed = discord.Embed(
            title="✅ Chat Channel Updated",
            description=f"Bot will now respond to all messages in {channel.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="Channel ID", value=str(channel.id), inline=False)
        await ctx.send(embed=embed)
        
        logger.info(f"Admin {ctx.author} set chat channel to {channel.name} ({channel.id})")
    
    @commands.command(name="unsetchannel")
    async def unset_chat_channel(self, ctx: commands.Context):
        """Remove specific chat channel restriction (Admin only)"""
        if not self.is_admin(ctx.author.id):
            await ctx.send("Only the bot admin can use this command!")
            return
        
        self.bot.config.chat_channel_id = None
        
        embed = discord.Embed(
            title="✅ Chat Channel Restriction Removed",
            description="Bot will now respond to mentions and DMs only",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        
        logger.info(f"Admin {ctx.author} removed chat channel restriction")
    
    @commands.command(name="setprefix")
    async def set_prefix(self, ctx: commands.Context, new_prefix: str):
        """Change the bot's command prefix (Admin only)"""
        if not self.is_admin(ctx.author.id):
            await ctx.send("Only the bot admin can use this command!")
            return
        
        if len(new_prefix) > 5:
            await ctx.send("Prefix must be 5 characters or less!")
            return
        
        old_prefix = self.bot.config.command_prefix
        self.bot.config.command_prefix = new_prefix
        self.bot.command_prefix = new_prefix
        
        embed = discord.Embed(
            title="✅ Prefix Updated",
            description=f"Command prefix changed from `{old_prefix}` to `{new_prefix}`",
            color=discord.Color.green()
        )
        embed.add_field(name="Example", value=f"`{new_prefix}help`", inline=False)
        await ctx.send(embed=embed)
        
        logger.info(f"Admin {ctx.author} changed prefix from {old_prefix} to {new_prefix}")
    
    @commands.command(name="botstats")
    async def admin_stats(self, ctx: commands.Context):
        """Show detailed bot statistics (Admin only)"""
        if not self.is_admin(ctx.author.id):
            await ctx.send("Only the bot admin can use this command!")
            return
        
        # Get chat statistics
        chat_stats = self.bot.chat_manager.get_stats()
        
        # Bot information
        embed = discord.Embed(
            title="🤖 Bot Statistics",
            color=discord.Color.purple()
        )
        
        # Basic info
        embed.add_field(
            name="Bot Info",
            value=f"**Name:** {self.bot.user.name}\n"
                  f"**ID:** {self.bot.user.id}\n"
                  f"**Guilds:** {len(self.bot.guilds)}\n"
                  f"**Users:** {len(self.bot.users)}",
            inline=True
        )
        
        # Configuration
        embed.add_field(
            name="Configuration",
            value=f"**Prefix:** `{self.bot.config.command_prefix}`\n"
                  f"**Chat Channel:** {f'<#{self.bot.config.chat_channel_id}>' if self.bot.config.chat_channel_id else 'None'}\n"
                  f"**Admin:** <@{self.bot.config.admin_user_id}>",
            inline=True
        )
        
        # Chat statistics
        embed.add_field(
            name="Chat Statistics",
            value=f"**Active Channels:** {chat_stats['total_channels']}\n"
                  f"**Active Users:** {chat_stats['total_users']}\n"
                  f"**Channel Messages:** {chat_stats['total_channel_messages']}\n"
                  f"**User Messages:** {chat_stats['total_user_messages']}",
            inline=False
        )
        
        # Server list
        server_list = "\n".join([f"• {guild.name} ({guild.member_count} members)" 
                                for guild in sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True)[:5]])
        if len(self.bot.guilds) > 5:
            server_list += f"\n... and {len(self.bot.guilds) - 5} more"
        
        embed.add_field(
            name="Top Servers",
            value=server_list,
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="clearall")
    async def clear_all_history(self, ctx: commands.Context):
        """Clear all chat history (Admin only)"""
        if not self.is_admin(ctx.author.id):
            await ctx.send("Only the bot admin can use this command!")
            return
        
        # Clear all histories
        self.bot.chat_manager.channel_histories.clear()
        self.bot.chat_manager.user_histories.clear()
        
        embed = discord.Embed(
            title="🗑️ All Chat History Cleared",
            description="All conversation histories have been reset",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        
        logger.info(f"Admin {ctx.author} cleared all chat history")
    
    @commands.command(name="shutdown")
    async def shutdown_bot(self, ctx: commands.Context):
        """Shutdown the bot (Admin only)"""
        if not self.is_admin(ctx.author.id):
            await ctx.send("Only the bot admin can use this command!")
            return
        
        embed = discord.Embed(
            title="🛑 Bot Shutting Down",
            description="Bot is shutting down gracefully...",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        
        logger.info(f"Admin {ctx.author} initiated bot shutdown")
        await self.bot.close()
    
    @commands.command(name="eval")
    async def eval_code(self, ctx: commands.Context, *, code: str):
        """Execute Python code (Admin only - use with caution)"""
        if not self.is_admin(ctx.author.id):
            await ctx.send("Only the bot admin can use this command!")
            return
        
        try:
            # Remove code blocks if present
            if code.startswith('```python'):
                code = code[9:-3]
            elif code.startswith('```'):
                code = code[3:-3]
            
            # Execute the code
            result = eval(code)
            
            embed = discord.Embed(
                title="💻 Code Execution Result",
                description=f"```python\n{code}\n```\n**Result:**\n```\n{result}\n```",
                color=discord.Color.green()
            )
        except Exception as e:
            embed = discord.Embed(
                title="❌ Code Execution Error",
                description=f"```python\n{code}\n```\n**Error:**\n```\n{str(e)}\n```",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)
        logger.info(f"Admin {ctx.author} executed code: {code[:50]}...")
    
    @commands.command(name="say")
    async def say_message(self, ctx: commands.Context, channel: Optional[discord.TextChannel], *, message: str):
        """Make the bot say something in a channel (Admin only)"""
        if not self.is_admin(ctx.author.id):
            await ctx.send("Only the bot admin can use this command!")
            return
        
        target_channel = channel or ctx.channel
        
        try:
            await target_channel.send(message)
            if target_channel != ctx.channel:
                await ctx.send(f"✅ Message sent to {target_channel.mention}")
        except discord.Forbidden:
            await ctx.send(f"❌ I don't have permission to send messages in {target_channel.mention}")
        except Exception as e:
            await ctx.send(f"❌ Error sending message: {str(e)}")
    
    @commands.command(name="reload")
    async def reload_cog(self, ctx: commands.Context, cog_name: str = None):
        """Reload bot cogs (Admin only)"""
        if not self.is_admin(ctx.author.id):
            await ctx.send("Only the bot admin can use this command!")
            return
        
        if not cog_name:
            await ctx.send("Available cogs: ChatCommands, FunCommands, AdminCommands")
            return
        
        try:
            # This is a simplified reload - in practice you'd need proper cog reloading
            await ctx.send(f"⚠️ Manual restart required to reload cogs")
        except Exception as e:
            await ctx.send(f"❌ Error reloading cog: {str(e)}")
    
    @commands.command(name="invite")
    async def invite_link(self, ctx: commands.Context):
        """Get bot invite link and support server"""
        embed = discord.Embed(
            title="🤖 Bot Invite & Support",
            color=discord.Color.blue()
        )
        
        # Generate invite link
        permissions = discord.Permissions()
        permissions.send_messages = True
        permissions.read_messages = True
        permissions.read_message_history = True
        permissions.embed_links = True
        permissions.add_reactions = True
        
        invite_url = discord.utils.oauth_url(self.bot.user.id, permissions=permissions)
        
        embed.add_field(
            name="📎 Invite Bot",
            value=f"[Click here to invite me!]({invite_url})",
            inline=False
        )
        
        embed.add_field(
            name="🆘 Support Server",
            value=f"[Join our support server]({self.bot.config.help_server_invite})",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Bot Info",
            value=f"**Powered by:** OpenRouter & DeepSeek\n"
                  f"**Prefix:** `{self.bot.config.command_prefix}`\n"
                  f"**Version:** 1.0.0",
            inline=False
        )
        
        await ctx.send(embed=embed)