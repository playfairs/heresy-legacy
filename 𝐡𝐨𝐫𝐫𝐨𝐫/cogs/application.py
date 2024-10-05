import discord
from discord.ext import commands

class Application(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Application cog has been initialized!")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Application cog loaded and bot is ready!")

        # Attempt to sync global commands
        try:
            synced = await self.bot.tree.sync()
            print(f"Successfully synced {len(synced)} application commands globally.")
        except Exception as e:
            print(f"Failed to sync application commands: {e}")

    @commands.command(name='auserinfo', help="Displays the user's information.")
    async def auserinfo(self, ctx):
        """Displays the information of the user who called the command."""
        print("Userinfo command invoked!")  # Debugging
        if ctx.guild:  # Ensure this command is not used in a server
            await ctx.send("This command is only usable outside of servers.")
            return

        user = ctx.author
        embed = discord.Embed(title="User Information", color=discord.Color.blue())
        embed.add_field(name="Username", value=user.name, inline=False)
        embed.add_field(name="User ID", value=user.id, inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name='aavatar', help="Displays the user's avatar.")
    async def aavatar(self, ctx):
        """Displays the avatar of the user who called the command."""
        print("Avatar command invoked!")  # Debugging
        if ctx.guild:  # Ensure this command is not used in a server
            await ctx.send("This command is only usable outside of servers.")
            return

        user = ctx.author
        embed = discord.Embed(title=f"{user.name}'s Avatar", color=discord.Color.blue())
        embed.set_image(url=user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name='abanner', help="Displays the user's banner.")
    async def abanner(self, ctx):
        """Displays the banner of the user who called the command."""
        print("Banner command invoked!")  # Debugging
        if ctx.guild:  # Ensure this command is not used in a server
            await ctx.send("This command is only usable outside of servers.")
            return

        user = await self.bot.fetch_user(ctx.author.id)  # Fetch full user object to access banner
        if user.banner:
            embed = discord.Embed(title=f"{user.name}'s Banner", color=discord.Color.blue())
            embed.set_image(url=user.banner.url)
        else:
            embed = discord.Embed(description="You do not have a banner set.", color=discord.Color.red())
        await ctx.send(embed=embed)

# Setup function to add the cog
async def setup(bot):
    # Check if the commands are already registered
    existing_commands = {command.name for command in bot.commands}

    # Only add commands that aren't already registered
    if 'auserinfo' not in existing_commands:
        await bot.add_cog(Application(bot))
    else:
        print("Application cog already has registered commands; skipping registration.")
