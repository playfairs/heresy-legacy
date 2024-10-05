import discord
from discord.ext import commands
import os
import asyncio

class IDLogger(commands.Cog):
    ALLOWED_USER_ID = 785042666475225109  # Replace this with your Discord user ID

    def __init__(self, bot):
        self.bot = bot
        self.directory_path = "ID Logger/UIDs"  # Directory path for storing the log files

        # Ensure the directories exist
        os.makedirs(self.directory_path, exist_ok=True)

    def cog_check(self, ctx):
        """Check if the command invoker is the allowed user, only for this cog."""
        if ctx.cog is self and ctx.author.id != self.ALLOWED_USER_ID:
            raise commands.CheckFailure(f"I know damn fuckin well, this nigga {ctx.author.mention} did not just try to use a client-side command.") 
        return True

    @commands.command(name="uid")
    async def uid_log(self, ctx, user: discord.Member):
        """Logs the mentioned user's ID into UIDs.txt file."""
        if ctx.author.id != self.ALLOWED_USER_ID:
            await ctx.send(f"You're not allowed to use this command, {ctx.author.mention}.")
            return

        file_path = os.path.join(self.directory_path, "UIDs.txt")

        # Append the user's ID to the file
        with open(file_path, 'a') as f:
            f.write(f"{user.id}\n")

        await ctx.send(f"User ID for {user.mention} has been logged in `UIDs.txt`.")

    @commands.command(name="uidban")
    async def uid_ban(self, ctx):
        """Asks for a .txt file and bans users whose UIDs are listed in it."""
        if ctx.author.id != self.ALLOWED_USER_ID:
            await ctx.send(f"You're not allowed to use this command, {ctx.author.mention}.")
            return

        await ctx.send(f"{ctx.author.mention}, please provide the `.txt` file containing the UIDs to be banned.")

        # Wait for the user to upload a .txt file
        def check(m):
            return m.author == ctx.author and m.attachments and m.attachments[0].filename.endswith('.txt')

        try:
            # Wait for the message response with the file
            message = await self.bot.wait_for('message', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            return await ctx.send(f"{ctx.author.mention}, you took too long to provide the file. Please try again.")

        # Get the file
        txt_file = message.attachments[0]
        banned_count = 0
        total_count = 0

        # Download and process the file
        await ctx.send("Scanning the provided file...")
        content = await txt_file.read()
        user_ids = content.decode('utf-8').splitlines()

        # Attempt to ban each user in the file
        for user_id in user_ids:
            try:
                # Ban the user if the ID is valid and the bot has permissions
                user_id = int(user_id)  # Convert ID to integer
                user = await self.bot.fetch_user(user_id)  # Fetch the user object
                await ctx.guild.ban(user, reason="Mass ban initiated via UID Logger.")
                banned_count += 1
            except Exception as e:
                print(f"Failed to ban {user_id}: {e}")
            
            total_count += 1

        await ctx.send(f"Scan complete, {banned_count}/{total_count} members have been banned.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handles errors for the cog."""
        if isinstance(error, commands.CheckFailure):
            await ctx.send(str(error))

# Async setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(IDLogger(bot))
