import discord
from discord.ext import commands

class VoiceChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='jvc')
    async def join_voice_channel(self, ctx):
        """Make the bot join the current voice channel."""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f'Joined {channel}.')
        else:
            await ctx.send("You need to be in a voice channel to use this command.")

    @commands.command(name='leave')
    async def leave_voice_channel(self, ctx):
        """Make the bot leave the voice channel."""
        if ctx.voice_client:  # Check if the bot is in a voice channel
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from voice channel.")
        else:
            await ctx.send("I'm not connected to any voice channel.")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for specific phrases to send invite links."""
        if message.author == self.bot.user:  # Ignore messages from the bot itself
            return

        if message.content.lower() in ["jvc", "join vc", "vc"]:
            if message.author.voice:
                channel = message.author.voice.channel
                invite = await channel.create_invite(max_age=300)  # Create an invite link
                await message.channel.send(invite)
            else:
                # Find the first available voice channel
                for guild in self.bot.guilds:
                    for vc in guild.voice_channels:
                        invite = await vc.create_invite(max_age=300)  # Create an invite link
                        await message.channel.send(invite)
                        return  # Exit after sending the invite to the first channel found
                await message.channel.send("No voice channels available.")

async def setup(bot):
    await bot.add_cog(VoiceChat(bot))
