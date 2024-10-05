import discord
from discord.ext import commands, tasks
from discord import app_commands

class Pic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.GUILD_ID = 961097369817071626  # Replace with your actual guild ID
        self.ROLE_ID = 1204232001389985814  # Replace with your actual "pic" role ID
        self.log_channel_id = 1286944011671830559  # Replace with your actual log channel ID

    # Status check task (not started automatically)
    @tasks.loop(seconds=10)
    async def check_online_status(self):
        await self.deep_scan_role_check()

    # Command to manually deep scan the server
    @app_commands.command(name="deepscan", description="Manually deep scan all members for '/heresy' status.")
    async def deepscan(self, interaction: discord.Interaction):
        await interaction.response.send_message("Starting manual deep scan of all users...", ephemeral=True)
        
        result = await self.deep_scan_role_check()
        await interaction.followup.send(result, ephemeral=True)

    # Helper function to perform the deep scan and role adjustment
    async def deep_scan_role_check(self):
        guild = self.bot.get_guild(self.GUILD_ID)
        if guild is None:
            return "Guild not found."

        await guild.chunk()  # Ensure all members are cached

        role = guild.get_role(self.ROLE_ID)
        if role is None:
            return "Role with the specified ID not found."

        log_channel = guild.get_channel(self.log_channel_id)
        if log_channel is None:
            return "Log channel not found."

        users_with_heresy = []
        users_without_heresy = []

        # Check all members and adjust roles
        for member in guild.members:
            has_heresy = False
            if member.raw_status in ['online', 'idle', 'dnd']:
                if member.activity and isinstance(member.activity, discord.CustomActivity):
                    if "/heresy" in member.activity.name:
                        has_heresy = True
                        users_with_heresy.append(member)

            # Adjust roles based on presence of "/heresy"
            if has_heresy and role not in member.roles:
                try:
                    await member.add_roles(role)
                    await log_channel.send(f"Gave pic perms to {member.mention}, user has '/heresy' in status")
                except discord.Forbidden:
                    print(f"Bot doesn't have permission to assign roles to {member.name}")
                except discord.HTTPException as e:
                    print(f"Failed to assign role due to HTTPException: {e}")

            # This is where we modify the logic
            # If user had "/heresy" but is now offline, keep the role
            elif not has_heresy and role in member.roles:
                if member.raw_status != 'offline':
                    try:
                        await member.remove_roles(role)
                        await log_channel.send(f"Removed pic perms from {member.mention}, user no longer has '/heresy' in status")
                    except discord.Forbidden:
                        print(f"Bot doesn't have permission to remove roles from {member.name}")
                    except discord.HTTPException as e:
                        print(f"Failed to remove role due to HTTPException: {e}")
                    users_without_heresy.append(member)
                else:
                    print(f"Skipping removal for {member.name} (offline but previously had '/heresy').")

        return (f"Deep scan complete. {len(users_with_heresy)} users have '/heresy' in their status, "
                f"{len(users_without_heresy)} users had the role removed.")

    # Slash command to start or stop the status check
    @app_commands.command(name="status", description="Start or stop the online status check.")
    @app_commands.describe(action="Choose to start or stop the online status check.")
    @app_commands.choices(action=[
        app_commands.Choice(name="start", value="start"),
        app_commands.Choice(name="stop", value="stop")
    ])
    async def manage_status(self, interaction: discord.Interaction, action: str):
        if action == "start":
            if not self.check_online_status.is_running():
                self.check_online_status.start()
                await interaction.response.send_message("Started online status check.")
            else:
                await interaction.response.send_message("Online status check is already running.")
        
        elif action == "stop":
            if self.check_online_status.is_running():
                self.check_online_status.stop()
                await interaction.response.send_message("Stopped online status check.")
            else:
                await interaction.response.send_message("No online status check is currently running.")

    # Command to display all users with "/heresy" in their status
    @commands.command(name="replist")
    async def replist(self, ctx):
        guild = self.bot.get_guild(self.GUILD_ID)
        if guild is None:
            await ctx.send("Guild not found.")
            return

        await guild.chunk()  # Ensure all members are cached

        users_with_heresy = []

        for member in guild.members:
            if member.raw_status in ['online', 'idle', 'dnd']:
                if member.activity and isinstance(member.activity, discord.CustomActivity):
                    if "/heresy" in member.activity.name:
                        users_with_heresy.append(member.mention)

        if users_with_heresy:
            await ctx.send(f"Users with `/heresy` in their status: {', '.join(users_with_heresy)}")
        else:
            await ctx.send("No users currently have `/heresy` in their status.")

    # Event listener for on_message to respond to "pic perms" requests
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return  # Prevent bot from replying to itself

        # Convert the message to lowercase for easier matching
        content = message.content.lower()

        # Check for variations of asking for "pic perms"
        if any(keyword in content for keyword in ["get pic perms", "give me pic", "give me pic perms", "how do i get pic perms", "pic perms"]):
            await message.channel.send("Rep `/heresy` in status for pic perms, or boost the server")

async def setup(bot):
    await bot.add_cog(Pic(bot))
