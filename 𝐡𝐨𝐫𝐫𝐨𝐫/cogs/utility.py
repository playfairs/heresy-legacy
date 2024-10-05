import discord
from discord import app_commands
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Pong! {round(self.bot.latency * 1000)}ms', ephemeral=True)

    @app_commands.command(name="userinfo", description="Get information about a user")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{member}'s Info", color=discord.Color.blue())
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Name", value=member.name)
        embed.add_field(name="Created At", value=member.created_at.strftime("%m/%d/%Y, %H:%M:%S"))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="av", description="Display a user's avatar.")
    @app_commands.describe(
        member="The member whose avatar you want to display",
        avatar_type="Choose between 'personal' or 'server' avatar"
    )
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None, avatar_type: str = "personal"):
        member = member or interaction.user  # Default to the user who invoked the command if no member is provided

        if avatar_type.lower() == "server" and member.guild_avatar:
            avatar_url = member.guild_avatar.url  # Display server-specific avatar if available
            embed = discord.Embed(title=f"{member.display_name}'s Server Avatar", color=discord.Color.blue())
        else:
            avatar_url = member.avatar.url  # Default to personal avatar
            embed = discord.Embed(title=f"{member.display_name}'s Personal Avatar", color=discord.Color.blue())

        embed.set_image(url=avatar_url)
        await interaction.response.send_message(embed=embed)

    # New banner command
    @app_commands.command(name="banner", description="Displays a user's banner.")
    async def banner(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user  # Default to the user who invoked the command if no member is provided

        # Fetching the user's banner
        user = await self.bot.fetch_user(member.id)
        banner_url = user.banner.url if user.banner else None

        embed = discord.Embed(title=f"{member.name}'s Banner", color=discord.Color.blue())
        if banner_url:
            embed.set_image(url=banner_url)
        else:
            embed.description = "This user does not have a banner set."

        await interaction.response.send_message(embed=embed)

# Setup function required for Cogs
async def setup(bot):
    await bot.add_cog(Utility(bot))
