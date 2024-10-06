import discord
from discord.ext import commands
import random

class Alphabet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # List of more casual, human-like phrases
        self.phrases = [
            "Yo, what's good?",
            "Nah, don't sweat it!",
            "Just chillin', y'know?",
            "Hey there! How's it going?",
            "LMAO, that's funny!",
            "You good?",
            "For real, I’m just vibin'.",
            "No worries, I got this!",
            "It is what it is, dude!",
            "Heyyy, how you doin'?",
            "What's up?",
            "I'm all ears, what's up?",
            "You got it!"
        ]

    @commands.command(name="reply", description="Make the bot respond with a human-like sentence.")
    async def reply_command(self, ctx):
        """Generates a human-like response using predefined phrases."""
        # Pick a random casual phrase from the list
        response = random.choice(self.phrases)
        await ctx.send(response)

# Async setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(Alphabet(bot))
