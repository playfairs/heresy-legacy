import discord
from discord.ext import commands
import aiohttp

class MirrorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mirrored_user = None  # Variable to store the mirrored user
        self.default_avatar_url = "https://i.ytimg.com/vi/bCy04PBoyS0/mqdefault.jpg"  # URL of the default avatar to revert to

    # Command to start mirroring a user and update the bot's avatar and nickname
    @commands.command(name='mirror')
    async def mirror_user(self, ctx, user: discord.Member):
        self.mirrored_user = user

        # Update bot's display name (nickname) to match the mirrored user's display name
        try:
            await ctx.guild.me.edit(nick=user.display_name)  # Change the bot's nickname to match the user
        except discord.Forbidden:
            await ctx.send("I don't have permission to change my nickname in this server.")
            return

        # Fetch and set the bot's avatar to match the user's avatar
        async with aiohttp.ClientSession() as session:
            async with session.get(str(user.display_avatar.url)) as response:
                if response.status == 200:
                    avatar_bytes = await response.read()
                    await self.bot.user.edit(avatar=avatar_bytes)  # Update the bot's avatar
                    await ctx.send(f"Now mirroring {user.mention} and updated the bot's display name and avatar to match theirs!")
                else:
                    await ctx.send(f"Failed to fetch {user.name}'s avatar. Starting mirroring without avatar change.")

    # Event listener to detect when the mirrored user sends a message and mirror their message
    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if a user is being mirrored and the message is not from a bot
        if self.mirrored_user and message.author == self.mirrored_user and not message.author.bot:
            if message.author == self.bot.user:
                return  # Prevent the bot from mirroring its own messages
            await message.channel.send(message.content)  # Mirror the message content

    # Command to stop mirroring the current user, reset avatar, and remove nickname
    @commands.command(name='stopmirror')
    async def stop_mirror(self, ctx):
        # Check if there is a mirrored user set
        if self.mirrored_user:
            await ctx.send(f"Stopped mirroring {self.mirrored_user.mention}.")
            self.mirrored_user = None  # Reset the mirrored user to None

            # Reset the bot's nickname
            try:
                await ctx.guild.me.edit(nick=None)  # Remove the bot's server nickname
            except discord.Forbidden:
                await ctx.send("I don't have permission to change my nickname in this server.")

            # Reset the bot's avatar to a default image
            async with aiohttp.ClientSession() as session:
                async with session.get(self.default_avatar_url) as response:
                    if response.status == 200:
                        avatar_bytes = await response.read()
                        await self.bot.user.edit(avatar=avatar_bytes)  # Update the bot's avatar
                        await ctx.send("Bot's avatar has been reset to the default image.")
                    else:
                        await ctx.send("Failed to reset bot's avatar to the default image.")
        else:
            await ctx.send("No user is currently being mirrored.")

# Async setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(MirrorCog(bot))
