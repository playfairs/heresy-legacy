import discord
from discord.ext import commands
from discord import app_commands
from collections import defaultdict
import time

class Antinuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.action_timestamps = defaultdict(list)
        self.trusted_roles = [1277350852767776951]  # List of trusted role IDs
        self.action_limits = {
            'ban': {'limit': 3, 'timeframe': 600},
            'kick': {'limit': 3, 'timeframe': 600},
            'role_modify': {'limit': 3, 'timeframe': 600},
            'channel_modify': {'limit': 3, 'timeframe': 600},
            'webhook_create': {'limit': 3, 'timeframe': 600},
            'bot_add_remove': {'limit': 1, 'timeframe': 600}
        }
        self.logging_channel_id = 1290013515163238431  # Set your logging channel ID here

    async def log_action(self, action_type, provoker, target, result, guild):
        # Create the embed for logging the action
        embed = discord.Embed(title="Antinuke Action Detected", color=discord.Color.red())
        embed.add_field(name="Action Type", value=action_type.capitalize(), inline=False)
        embed.add_field(name="Provoker", value=f"{provoker.name}#{provoker.discriminator}", inline=True)
        embed.add_field(name="Target", value=f"{target.name}#{target.discriminator}", inline=True)
        embed.add_field(name="Action Result", value=result, inline=False)
        embed.set_footer(text=f"Guild: {guild.name} | Guild ID: {guild.id}")

        # Get the logging channel and send the embed
        logging_channel = guild.get_channel(self.logging_channel_id)
        if logging_channel:
            await logging_channel.send(embed=embed)

    async def check_action(self, guild, user, action_type, target=None):
        # Check if the user has a trusted role
        if any(role.id in self.trusted_roles for role in user.roles):
            return  # Trusted user, no action needed

        current_time = time.time()
        self.action_timestamps[guild.id].append((action_type, current_time))

        # Remove timestamps older than the timeframe for each action type
        self.action_timestamps[guild.id] = [
            (action, timestamp) 
            for action, timestamp in self.action_timestamps[guild.id] 
            if timestamp > current_time - self.action_limits[action]['timeframe']
        ]

        # Count actions of the same type
        action_count = sum(1 for action, _ in self.action_timestamps[guild.id] if action == action_type)
        
        # Check if action limit is exceeded
        if action_count > self.action_limits[action_type]['limit']:
            # Take action against the user (provoker)
            await guild.kick(user)  # or `guild.ban(user)` if you prefer
            result = f"{user.name} was kicked for exceeding {action_type} action limits!"
            await self.log_action(action_type, user, target, result, guild)  # Log the action with the embed
            print(result)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        provoker = guild.get_member(user.id)  # Provoker (the one who banned the user) should be identified through an audit log in real scenarios
        await self.check_action(guild, provoker, "ban", user)
        await self.log_action("ban", provoker, user, "Ban action detected and handled", guild)  # Log the ban action

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        provoker = member.guild.get_member(member.id)  # Provoker needs to be identified
        await self.check_action(member.guild, provoker, "kick", member)
        await self.log_action("kick", provoker, member, "Kick action detected and handled", member.guild)  # Log the kick action

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        provoker = before.guild.owner  # Provoker should be identified using audit logs
        await self.check_action(before.guild, provoker, "role_modify", after.guild)
        await self.log_action("role_modify", provoker, after.guild, "Role modification action detected and handled", before.guild)  # Log the role modification

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        provoker = before.guild.owner  # Provoker needs to be correctly identified
        await self.check_action(before.guild, provoker, "channel_modify", after.guild)
        await self.log_action("channel_modify", provoker, after.guild, "Channel modification action detected and handled", before.guild)  # Log the channel modification

    @commands.Cog.listener()
    async def on_webhook_create(self, webhook):
        provoker = webhook.user  # Provoker is the user who created the webhook
        await self.check_action(webhook.guild, provoker, "webhook_create", webhook.user)
        await self.log_action("webhook_create", provoker, webhook.user, "Webhook creation action detected and handled", webhook.guild)  # Log the webhook creation

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if before.owner_id != after.owner_id:  # Indicates a bot has been added or removed
            provoker = after.owner  # Provoker is the new owner of the guild
            await self.check_action(before, provoker, "bot_add_remove", after.owner)
            await self.log_action("bot_add_remove", provoker, after.owner, "Bot add/remove action detected and handled", before)  # Log the bot add/remove action

    @commands.Cog.listener()
    async def on_ready(self):
        print("Antinuke cog loaded!")

# To set up the cog
async def setup(bot):
    await bot.add_cog(Antinuke(bot))
