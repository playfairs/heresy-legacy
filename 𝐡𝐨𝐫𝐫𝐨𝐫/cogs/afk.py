import discord
from discord.ext import commands
import sqlite3
import time

# Define a class for the AFK cog
class AFKCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.initialize_db()
        print("[AFKCog] Initialized AFK cog and database connection.")

    def initialize_db(self):
        """Initialize the database to store AFK users."""
        try:
            conn = sqlite3.connect('afk_users.db')
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS afk_users (
                user_id INTEGER PRIMARY KEY,
                reason TEXT,
                afk_time INTEGER
            )
            ''')
            conn.commit()
            conn.close()
            print("[AFKCog] Database initialized successfully.")
        except sqlite3.Error as e:
            print(f"[AFKCog] Error initializing database: {e}")

    def set_afk(self, user_id, reason):
        """Sets the AFK status for a user with the current timestamp."""
        try:
            conn = sqlite3.connect('afk_users.db')
            cursor = conn.cursor()
            cursor.execute('''
            INSERT OR REPLACE INTO afk_users (user_id, reason, afk_time)
            VALUES (?, ?, ?)
            ''', (user_id, reason, int(time.time())))
            conn.commit()
            conn.close()
            print(f"[AFKCog] AFK set for user {user_id} with reason: {reason}")
        except sqlite3.Error as e:
            print(f"[AFKCog] Error setting AFK: {e}")

    def get_afk_status(self, user_id):
        """Gets the AFK status and timestamp for a user."""
        try:
            conn = sqlite3.connect('afk_users.db')
            cursor = conn.cursor()
            cursor.execute('''
            SELECT reason, afk_time FROM afk_users WHERE user_id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result
        except sqlite3.Error as e:
            print(f"[AFKCog] Error getting AFK status: {e}")
            return None

    def remove_afk(self, user_id):
        """Removes the AFK status for a user."""
        try:
            conn = sqlite3.connect('afk_users.db')
            cursor = conn.cursor()
            cursor.execute('''
            DELETE FROM afk_users WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
            conn.close()
            print(f"[AFKCog] AFK removed for user {user_id}.")
        except sqlite3.Error as e:
            print(f"[AFKCog] Error removing AFK: {e}")

    def format_time_ago(self, afk_time):
        """Formats the time since the AFK status was set."""
        time_elapsed = int(time.time()) - afk_time
        if time_elapsed < 60:
            return "a few seconds ago"
        elif time_elapsed < 3600:  # Less than 1 hour
            minutes = time_elapsed // 60
            return f"{minutes} minutes ago"
        elif time_elapsed < 86400:  # Less than 24 hours
            hours = time_elapsed // 3600
            return f"{hours} hours ago"
        else:
            days = time_elapsed // 86400
            return f"{days} days ago"

    @commands.command(name='afk')
    async def afk(self, ctx, *, reason: str = "AFK"):
        """Set the AFK status with an optional reason."""
        user_id = ctx.author.id
        self.set_afk(user_id, reason)

        embed = discord.Embed(
            title=f"{ctx.author.display_name}",
            description=f"I have set your AFK to: {reason}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="You are now AFK.")
        await ctx.reply(embed=embed, mention_author=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages or messages that don't originate from a user
        if message.author.bot or message.webhook_id is not None:
            return

        # Check if the message is a command and ignore it
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            print(f"[Debug] Ignoring AFK removal for command: {message.content}")
            return

        # Log the message details for debugging purposes
        print(f"[Debug] Message received: {message.content} from {message.author} (ID: {message.author.id})")

        # Check if the author is AFK
        afk_data = self.get_afk_status(message.author.id)
        
        if afk_data:
            print(f"[Debug] Removing AFK for user: {message.author.id} due to manual message.")
            self.remove_afk(message.author.id)

            embed = discord.Embed(
                title=f"Welcome back, {message.author.display_name}!",
                description="I have removed your AFK status.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"You were AFK for {self.format_time_ago(afk_data[1])}.")
            await message.channel.send(embed=embed)

        # Check for mentioned users who are AFK and notify the sender
        for mentioned_user in message.mentions:
            afk_data = self.get_afk_status(mentioned_user.id)
            if afk_data:
                embed = discord.Embed(
                    title=f"{mentioned_user.display_name} is currently AFK.",
                    description=f"Reason: {afk_data[0]}\nAFK since {self.format_time_ago(afk_data[1])}.",
                    color=discord.Color.orange()
                )
                await message.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # Ignore edits by bots or if there's no meaningful content change
        if after.author.bot or before.content == after.content:
            return

        print(f"[Debug] Message edited by {after.author.display_name} (ID: {after.author.id}).")

        afk_data = self.get_afk_status(after.author.id)
        if afk_data:
            print(f"[Debug] Removing AFK for user: {after.author.id} due to message edit.")
            self.remove_afk(after.author.id)

            embed = discord.Embed(
                title=f"Welcome back, {after.author.display_name}!",
                description="I have removed your AFK status.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"You were AFK for {self.format_time_ago(afk_data[1])}.")
            await after.channel.send(embed=embed)

# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(AFKCog(bot))
    print("[AFKCog] AFK cog loaded successfully.")
