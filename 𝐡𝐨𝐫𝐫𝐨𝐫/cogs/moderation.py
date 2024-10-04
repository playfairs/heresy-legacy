import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Register the slash commands using @app_commands.command()
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        await member.kick(reason=reason)
        await interaction.response.send_message(f'Kicked {member.mention} for reason: {reason}', ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        await member.ban(reason=reason)
        await interaction.response.send_message(f'Banned {member.mention} for reason: {reason}', ephemeral=True)

    @app_commands.command(name="unban", description="Unban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, member_name: str):
        banned_users = await interaction.guild.bans()
        member_name, member_discriminator = member_name.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.name == member_name and user.discriminator == member_discriminator:
                await interaction.guild.unban(user)
                await interaction.response.send_message(f'Unbanned {user.mention}', ephemeral=True)
                return
        await interaction.response.send_message(f'Member {member_name}#{member_discriminator} not found', ephemeral=True)

# Setup function required for Cogs
async def setup(bot):
    await bot.add_cog(Moderation(bot))
