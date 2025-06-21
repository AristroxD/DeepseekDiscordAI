"""
Fun and entertainment commands for the Discord bot
"""

import asyncio
import random
import logging
from typing import List, Dict, Any
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

class FunCommands(commands.Cog):
    """Fun and entertainment commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_games: Dict[int, Dict[str, Any]] = {}
        
    @commands.command(name="joke")
    async def joke_command(self, ctx: commands.Context):
        """Tell a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why don't skeletons fight each other? They don't have the guts!",
            "What do you call a sleeping bull? A bulldozer!",
            "Why did the coffee file a police report? It got mugged!",
            "What's the best thing about Switzerland? I don't know, but the flag is a big plus!"
        ]
        
        joke = random.choice(jokes)
        embed = discord.Embed(
            title="😂 Random Joke",
            description=joke,
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="fun")
    async def fun_command(self, ctx: commands.Context):
        """Random fun activities"""
        activities = [
            "🎲 Roll a dice: You got a **{}**!",
            "🪙 Flip a coin: It's **{}**!",
            "🌟 Your luck today: **{}**/10",
            "🎯 Random fact: Did you know that honey never spoils?",
            "🎯 Random fact: A group of flamingos is called a 'flamboyance'!",
            "🎯 Random fact: Octopuses have three hearts!",
            "🔮 Magic 8-Ball says: **{}**"
        ]
        
        activity = random.choice(activities)
        
        if "dice" in activity:
            result = activity.format(random.randint(1, 6))
        elif "coin" in activity:
            result = activity.format(random.choice(["Heads", "Tails"]))
        elif "luck" in activity:
            result = activity.format(random.randint(1, 10))
        elif "Magic 8-Ball" in activity:
            responses = ["Yes", "No", "Maybe", "Ask again later", "Definitely", "Not likely", "Absolutely"]
            result = activity.format(random.choice(responses))
        else:
            result = activity
        
        embed = discord.Embed(
            title="🎉 Fun Activity",
            description=result,
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="game")
    async def game_command(self, ctx: commands.Context, game_type: str = None):
        """Start a mini-game"""
        if not game_type:
            embed = discord.Embed(
                title="🎮 Available Games",
                description="Use `!game <type>` to start:\n\n"
                          "• `trivia` - Answer trivia questions\n"
                          "• `math` - Solve math problems\n"
                          "• `word` - Word association game\n"
                          "• `riddle` - Solve riddles",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return
        
        if game_type.lower() == "trivia":
            await self.start_trivia(ctx)
        elif game_type.lower() == "math":
            await self.start_math_game(ctx)
        elif game_type.lower() == "word":
            await self.start_word_game(ctx)
        elif game_type.lower() == "riddle":
            await self.start_riddle_game(ctx)
        else:
            await ctx.send("Unknown game type! Use `!game` to see available games.")
    
    async def start_trivia(self, ctx: commands.Context):
        """Start a trivia game"""
        questions = [
            {"q": "What is the capital of France?", "a": "paris"},
            {"q": "What is 2 + 2?", "a": "4"},
            {"q": "What planet is known as the Red Planet?", "a": "mars"},
            {"q": "Who painted the Mona Lisa?", "a": "leonardo da vinci"},
            {"q": "What is the largest ocean on Earth?", "a": "pacific"}
        ]
        
        question = random.choice(questions)
        
        embed = discord.Embed(
            title="🧠 Trivia Question",
            description=f"**{question['q']}**\n\nYou have 30 seconds to answer!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        try:
            answer = await self.bot.wait_for('message', timeout=30.0, check=check)
            if answer.content.lower().strip() == question['a']:
                await ctx.send("🎉 Correct! Well done!")
            else:
                await ctx.send(f"❌ Wrong! The answer was: **{question['a']}**")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Time's up! The answer was: **{question['a']}**")
    
    async def start_math_game(self, ctx: commands.Context):
        """Start a math game"""
        num1 = random.randint(1, 50)
        num2 = random.randint(1, 50)
        operation = random.choice(['+', '-', '*'])
        
        if operation == '+':
            answer = num1 + num2
        elif operation == '-':
            answer = num1 - num2
        else:  # multiplication
            answer = num1 * num2
        
        embed = discord.Embed(
            title="🔢 Math Challenge",
            description=f"**{num1} {operation} {num2} = ?**\n\nYou have 30 seconds!",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        try:
            user_answer = await self.bot.wait_for('message', timeout=30.0, check=check)
            if user_answer.content.strip() == str(answer):
                await ctx.send("🎉 Correct! Great math skills!")
            else:
                await ctx.send(f"❌ Wrong! The answer was: **{answer}**")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Time's up! The answer was: **{answer}**")
    
    async def start_word_game(self, ctx: commands.Context):
        """Start a word association game"""
        words = ["cat", "sun", "book", "music", "ocean", "mountain", "flower", "computer", "friendship", "adventure"]
        word = random.choice(words)
        
        embed = discord.Embed(
            title="💭 Word Association",
            description=f"Give me a word that relates to: **{word}**\n\nBe creative!",
            color=discord.Color.teal()
        )
        await ctx.send(embed=embed)
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        try:
            response = await self.bot.wait_for('message', timeout=30.0, check=check)
            await ctx.send(f"Nice association! **{word}** → **{response.content}** 🌟")
        except asyncio.TimeoutError:
            await ctx.send("⏰ Time's up! Maybe next time!")
    
    async def start_riddle_game(self, ctx: commands.Context):
        """Start a riddle game"""
        riddles = [
            {"q": "I speak without a mouth and hear without ears. I have no body, but come alive with wind. What am I?", "a": "echo"},
            {"q": "The more you take, the more you leave behind. What am I?", "a": "footsteps"},
            {"q": "I'm tall when I'm young, and short when I'm old. What am I?", "a": "candle"},
            {"q": "What has keys but no locks, space but no room, and you can enter but not go inside?", "a": "keyboard"},
            {"q": "What gets wetter as it dries?", "a": "towel"}
        ]
        
        riddle = random.choice(riddles)
        
        embed = discord.Embed(
            title="🤔 Riddle Time",
            description=f"**{riddle['q']}**\n\nYou have 60 seconds to think!",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        try:
            answer = await self.bot.wait_for('message', timeout=60.0, check=check)
            if riddle['a'].lower() in answer.content.lower():
                await ctx.send("🎉 Excellent! You solved the riddle!")
            else:
                await ctx.send(f"❌ Good try! The answer was: **{riddle['a']}**")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Time's up! The answer was: **{riddle['a']}**")
    
    @commands.command(name="guess")
    async def guess_command(self, ctx: commands.Context, max_num: int = 100):
        """Start a number guessing game"""
        if max_num < 10 or max_num > 1000:
            await ctx.send("Please choose a number between 10 and 1000!")
            return
        
        secret_number = random.randint(1, max_num)
        attempts = 0
        max_attempts = min(10, max_num // 10 + 3)
        
        embed = discord.Embed(
            title="🎯 Number Guessing Game",
            description=f"I'm thinking of a number between 1 and {max_num}!\n"
                       f"You have {max_attempts} attempts. Good luck!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        while attempts < max_attempts:
            try:
                guess_msg = await self.bot.wait_for('message', timeout=30.0, check=check)
                
                try:
                    guess = int(guess_msg.content.strip())
                except ValueError:
                    await ctx.send("Please enter a valid number!")
                    continue
                
                attempts += 1
                
                if guess == secret_number:
                    await ctx.send(f"🎉 Congratulations! You guessed it in {attempts} attempts!")
                    return
                elif guess < secret_number:
                    remaining = max_attempts - attempts
                    await ctx.send(f"📈 Too low! {remaining} attempts remaining.")
                else:
                    remaining = max_attempts - attempts
                    await ctx.send(f"📉 Too high! {remaining} attempts remaining.")
                
                if attempts >= max_attempts:
                    await ctx.send(f"💔 Game over! The number was **{secret_number}**")
                    return
                    
            except asyncio.TimeoutError:
                await ctx.send(f"⏰ Time's up! The number was **{secret_number}**")
                return
    
    @commands.command(name="roll")
    async def roll_command(self, ctx: commands.Context, sides: int = 6):
        """Roll a dice with specified sides"""
        if sides < 2 or sides > 100:
            await ctx.send("Please choose between 2 and 100 sides!")
            return
        
        result = random.randint(1, sides)
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"Rolling a {sides}-sided die...\n\n**Result: {result}**",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="flip")
    async def flip_command(self, ctx: commands.Context):
        """Flip a coin"""
        result = random.choice(["Heads", "Tails"])
        emoji = "🟡" if result == "Heads" else "⚫"
        
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"Flipping a coin...\n\n{emoji} **{result}**",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)