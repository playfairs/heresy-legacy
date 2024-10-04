import discord
from discord.ext import commands
import os
from datetime import datetime
import asyncio

class MessageLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Create the main "Message Logger" directory if it doesn't exist
        self.main_directory = "Message Logger"
        if not os.path.exists(self.main_directory):
            os.makedirs(self.main_directory)
            print(f"[Debug] Created main directory: {self.main_directory}")
        else:
            print(f"[Debug] Main directory already exists: {self.main_directory}")

        # Create the "Logs" subfolder inside "Message Logger" if it doesn't exist
        self.logs_directory = os.path.join(self.main_directory, "Logs")
        if not os.path.exists(self.logs_directory):
            os.makedirs(self.logs_directory)
            print(f"[Debug] Created logs directory: {self.logs_directory}")
        else:
            print(f"[Debug] Logs directory already exists: {self.logs_directory}")

        # Print the full path for debugging purposes
        print(f"[Debug] Full logs directory path: {os.path.abspath(self.logs_directory)}")

    def log_message(self, message: discord.Message, action: str):
        """Logs a message action (sent or deleted) to a text file inside the Logs subfolder."""
        # Format the timestamp as [hh:mm AM/PM mm/dd/yy]
        timestamp = datetime.now().strftime("[%I:%M %p %m/%d/%y]")
        log_entry = f"<{message.id}> {timestamp} {action}: {message.content}\n"

        # Create the file path using the Logs directory and the user's username
        file_path = os.path.join(self.logs_directory, f"{message.author.name}.txt")

        # Print debug information
        print(f"[Debug] Attempting to write to file: {file_path}")

        try:
            # Open the file in append mode and write the log entry
            with open(file_path, "a", encoding="utf-8") as log_file:
                log_file.write(log_entry)
            print(f"[Debug] Log entry added for {message.author.name}: {log_entry}")
        except Exception as e:
            print(f"[Error] Failed to log message for {message.author.name}: {e}")
            # Print the full file path and directory to ensure correctness
            print(f"[Error] Full file path attempted: {file_path}")
            print(f"[Error] Directory listing of logs directory: {os.listdir(self.logs_directory)}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from the bot itself
        if message.author.bot:
            return

        print(f"[Debug] Message received: {message.content} from {message.author} (ID: {message.author.id})")

        # Log the sent message
        self.log_message(message, "Message Sent")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        # Ignore deleted messages from the bot itself
        if message.author.bot:
            return

        print(f"[Debug] Message deleted: {message.content} from {message.author} (ID: {message.author.id})")

        # Log the deleted message
        self.log_message(message, "Message Deleted")

    @commands.command(name="mIDNuke")
    async def mid_nuke(self, ctx):
        """Initiates the Message ID Nuke process for messages listed in a provided .txt file."""
        # Ask the user to upload a .txt file
        await ctx.send(f"{ctx.author.mention} Please upload the .txt file containing the message IDs to be nuked.")

        # Wait for the user to upload a file in the same channel
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.attachments

        try:
            # Wait for the message containing the .txt file
            txt_message = await self.bot.wait_for("message", timeout=60.0, check=check)
            txt_file = txt_message.attachments[0]

            # Check if the file is a .txt file
            if not txt_file.filename.endswith(".txt"):
                await ctx.send("Error: Please upload a .txt file.")
                return

            # Download the .txt file
            file_path = os.path.join(self.logs_directory, txt_file.filename)
            await txt_file.save(file_path)
            await ctx.send("Message ID file received. Processing...")

            # Read the file and extract message IDs
            with open(file_path, "r", encoding="utf-8") as file:
                message_ids = [line.split(">")[0].strip("<") for line in file.readlines() if line.startswith("<")]

            # Notify the user that the nuking process is starting
            await ctx.send("Message ID Nuking in progress, this may take a few minutes...")

            # Loop through the message IDs and try to delete them
            nuke_count = 0
            for msg_id in message_ids:
                try:
                    # Convert the message ID to an integer and attempt to delete it
                    msg_id = int(msg_id)
                    message = await ctx.fetch_message(msg_id)
                    await message.delete()
                    nuke_count += 1
                    print(f"[Debug] Deleted message ID: {msg_id}")
                except discord.NotFound:
                    print(f"[Error] Message ID {msg_id} not found, skipping...")
                except discord.Forbidden:
                    print(f"[Error] Missing permissions to delete message ID {msg_id}, skipping...")
                except Exception as e:
                    print(f"[Error] Failed to delete message ID {msg_id}: {e}")

            # Send a confirmation message once the process is complete
            await ctx.send(f"Nuking complete. Deleted {nuke_count}/{len(message_ids)} messages.")

        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} You took too long to upload the file. Please try the command again.")

async def setup(bot):
    await bot.add_cog(MessageLogger(bot))
