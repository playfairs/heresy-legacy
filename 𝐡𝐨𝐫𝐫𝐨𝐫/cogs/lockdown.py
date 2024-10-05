import discord
from discord.ext import commands
from discord import app_commands

# Global variables to store original permissions and admin roles
original_permissions = {}
original_admins = {}

class Lockdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kill", description="Lock down all channels and temporarily demote Admins to Staff role.")
    async def kill(self, interaction: discord.Interaction):
        """Lock down all channels and temporarily demote Admins to Staff role."""
        await interaction.response.defer()  # Defer the interaction

        guild = interaction.guild

        # Check if the user has the Administrator permission
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You don't have permission to use this command!", ephemeral=True)
            return

        # Specify the role ID that will be assigned to Admins during lockdown
        staff_role_id = 1288950729016606721  # Replace with your specific Staff role ID
        staff_role = guild.get_role(staff_role_id)

        if not staff_role:
            await interaction.followup.send("The specified Staff role ID does not exist in the server.", ephemeral=True)
            return

        # Step 1: Lock down all text channels by modifying "Send Messages" permission for roles in each channel
        global original_permissions
        original_permissions = {}

        for channel in guild.text_channels:  # Iterate only through text channels
            original_permissions[channel.id] = {}  # Create a dict entry for each channel

            # Iterate through the permissions overwrites of the channel
            for role_or_member, overwrite in channel.overwrites.items():
                # Check if the overwrite is for a role and has a Send Messages permission set
                if isinstance(role_or_member, discord.Role) and overwrite.send_messages is not None:
                    # Save the current permission state
                    original_permissions[channel.id][role_or_member.id] = overwrite.send_messages

                    # Set the Send Messages permission to False for roles with Send Messages allowed
                    if overwrite.send_messages:
                        new_overwrite = channel.overwrites_for(role_or_member)
                        new_overwrite.send_messages = False
                        await channel.set_permissions(role_or_member, overwrite=new_overwrite)

        # Step 2: Demote Admins to Staff role and keep track of original roles
        global original_admins
        original_admins = {}
        for member in guild.members:
            if member.bot:
                continue  # Skip bots

            # Check if the member has the Administrator permission
            if member.guild_permissions.administrator:
                try:
                    # Store the original roles of the member
                    original_admins[member.id] = [role.id for role in member.roles]

                    # Remove all roles and add the specific Staff role
                    await member.edit(roles=[staff_role])
                except Exception as e:
                    print(f"Failed to modify roles for {member.name}: {e}")

        await interaction.followup.send("All channels have been locked down and all users with Admin have been demoted to the specified role until the lockdown is lifted.", ephemeral=False)

    @app_commands.command(name="restore", description="Restore all channels and reassign original Admin roles.")
    async def restore(self, interaction: discord.Interaction):
        """Restore all channels and reassign original Admin roles."""
        await interaction.response.defer()  # Defer the interaction

        guild = interaction.guild

        # Check if the user has the Administrator permission
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You don't have permission to use this command!", ephemeral=True)
            return

        # Step 1: Restore original permissions in each channel
        for channel_id, permissions in original_permissions.items():
            channel = guild.get_channel(channel_id)
            if channel:
                for role_id, send_messages in permissions.items():
                    role = guild.get_role(role_id)
                    if role:
                        overwrite = channel.overwrites_for(role)
                        overwrite.send_messages = send_messages
                        await channel.set_permissions(role, overwrite=overwrite)

        # Step 2: Restore Admin roles to members who were demoted
        for member_id, role_ids in original_admins.items():
            member = guild.get_member(member_id)
            if member:
                roles = [guild.get_role(role_id) for role_id in role_ids if guild.get_role(role_id)]
                try:
                    await member.edit(roles=roles)
                except Exception as e:
                    print(f"Failed to restore roles for {member.name}: {e}")

        await interaction.followup.send("All channels and Admin roles have been restored to their original states.", ephemeral=False)

        # Clear the stored permissions and admins data
        original_permissions.clear()
        original_admins.clear()

    @app_commands.command(name="lockdown", description="Lock down all channels without modifying Admin roles.")
    async def lockdown(self, interaction: discord.Interaction):
        """Lock down all channels without modifying Admin roles."""
        await interaction.response.defer()  # Defer the interaction

        guild = interaction.guild

        # Check if the user has the Administrator permission
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You don't have permission to use this command!", ephemeral=True)
            return

        # Step 1: Lock down all text channels by modifying "Send Messages" permission for roles in each channel
        global original_permissions
        original_permissions = {}

        for channel in guild.text_channels:  # Iterate only through text channels
            original_permissions[channel.id] = {}  # Create a dict entry for each channel

            # Iterate through the permissions overwrites of the channel
            for role_or_member, overwrite in channel.overwrites.items():
                # Check if the overwrite is for a role and has a Send Messages permission set
                if isinstance(role_or_member, discord.Role) and overwrite.send_messages is not None:
                    # Save the current permission state
                    original_permissions[channel.id][role_or_member.id] = overwrite.send_messages

                    # Set the Send Messages permission to False for roles with Send Messages allowed
                    if overwrite.send_messages:
                        new_overwrite = channel.overwrites_for(role_or_member)
                        new_overwrite.send_messages = False
                        await channel.set_permissions(role_or_member, overwrite=new_overwrite)

        await interaction.followup.send("All channels have been locked down.", ephemeral=False)


# Function to set up the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(Lockdown(bot))
