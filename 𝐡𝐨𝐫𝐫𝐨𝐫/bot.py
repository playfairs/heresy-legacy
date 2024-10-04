import discord
from discord.ext import commands
import json
import os

# Load config.json for bot settings
with open('config.json') as config_file:
    config = json.load(config_file)

# Enable all intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config["prefix"], intents=intents)  # Prefix can be optional here

@bot.command(name="status")
async def set_custom_status(ctx, *, status: str):
    """Set the bot's custom status (activity)."""
    # Replace YOUR_USER_ID with the actual user ID you want to allow
    allowed_user_id = 785042666475225109  # e.g., 123456789012345678
    
    # Check if the command invoker's ID matches the allowed user ID
    if ctx.author.id != allowed_user_id:
        await ctx.send("You must be the owner of this bot to use this command.")
        return
    
    try:
        # Set the bot's presence to a custom status
        await bot.change_presence(activity=discord.CustomActivity(name=status))
        await ctx.send(f"Custom status changed to: {status}")
    except Exception as e:
        await ctx.send(f"Failed to change custom status: {e}")

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    # You can also set an initial custom status here if you like
    await bot.change_presence(activity=discord.CustomActivity(name="Initial Status"))


# Load cogs on bot startup
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Loaded Cog: {filename[:-3]}')
    print("Bot is ready and connected.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Loaded Cog: {filename[:-3]}') # that is chatgpt for sure xD
            

    # Sync the slash commands globally or to a specific guild
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands successfully.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    print("Bot is ready and connected.")

joins_log_channel_id = 1286944011671830559  # Replace with your actual log channel ID

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"{member.mention} Welcome, if you want to invite friends, you can. also rep /playfair in status if you want pic perms")

@bot.event
async def on_member_remove(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"damn {member.mention} left, they prolly wont be back")

@bot.command()
async def set_log_channel(ctx, channel: discord.TextChannel):
    global log_channel_id
    log_channel_id = channel.id
    await ctx.send(f'Log channel set to: {channel.mention}')

# Run the bot
bot.run(config["token"])