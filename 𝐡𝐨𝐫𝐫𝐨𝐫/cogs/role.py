import discord
from discord.ext import commands
from discord import app_commands


class RoleCmds(app_commands.Group):
    def __init__(self):
        # Initialize the Group with the name 'role' and a description
        super().__init__(name="role", description="Manage server roles")

    @app_commands.command(name="create", description="Create a new role in the server")
    async def role_create(self, interaction: discord.Interaction, role_name: str):
        """Creates a new role with the specified name."""
        guild = interaction.guild
        await guild.create_role(name=role_name)
        await interaction.response.send_message(f"Role '{role_name}' created successfully.", ephemeral=True)

    @app_commands.command(name="delete", description="Delete a role from the server")
    async def role_delete(self, interaction: discord.Interaction, role: discord.Role):
        """Deletes a specified role from the server."""
        await role.delete()
        await interaction.response.send_message(f"Role '{role.name}' has been deleted.", ephemeral=True)

    @app_commands.command(name="give", description="Give a role to a member")
    async def role_give(self, interaction: discord.Interaction, role: discord.Role, member: discord.Member):
        """Gives a specified role to a member."""
        await member.add_roles(role)
        await interaction.response.send_message(f"Role '{role.name}' has been given to {member.display_name}.", ephemeral=True)

    @app_commands.command(name="remove", description="Remove a role from a member")
    async def role_remove(self, interaction: discord.Interaction, role: discord.Role, member: discord.Member):
        """Removes a specified role from a member."""
        await member.remove_roles(role)
        await interaction.response.send_message(f"Role '{role.name}' has been removed from {member.display_name}.", ephemeral=True)

    @app_commands.command(name="rename", description="Rename a role in the server")
    async def role_rename(self, interaction: discord.Interaction, role: discord.Role, new_name: str):
        """Renames a specified role in the server."""
        await role.edit(name=new_name)
        await interaction.response.send_message(f"Role '{role.name}' has been renamed to '{new_name}'.", ephemeral=True)


# Set up the cog and register the command group
async def setup(bot: commands.Bot):
    bot.tree.add_command(RoleCmds())