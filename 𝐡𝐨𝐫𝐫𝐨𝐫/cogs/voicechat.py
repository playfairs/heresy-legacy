import discord
from discord.ext import commands

class VoiceChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return  # Ignore messages from the bot itself

        # Check for the trigger phrases
        if message.content.lower() in ["jvc", "join vc"]:
            if message.author.voice:
                channel = message.author.voice.channel
                invite = await channel.create_invite(max_age=300)  # Link expires in 5 minutes
                await message.channel.send(f"{channel.name}: {invite}")
            else:
                await message.channel.send("You need to be in a voice channel to create an invite!")

# Async setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(VoiceChatCog(bot))
