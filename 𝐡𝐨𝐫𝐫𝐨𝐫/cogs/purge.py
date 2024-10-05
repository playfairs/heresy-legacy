import discord
from discord.ext import commands
import asyncio

class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="purge")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        """Purges a specified number of messages from the channel (1-1000)."""
        if 1 <= amount <= 1000:
            deleted = await ctx.channel.purge(limit=amount)
            await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)
        else:
            await ctx.send("Please enter a valid amount between 1 and 1000.")

    @commands.command(name="bc")
    @commands.has_permissions(manage_messages=True)
    async def bc(self, ctx):
        """Purges recent bot commands in the last 10 minutes."""
        time_limit = 600  # 10 minutes in seconds
        deleted = await ctx.channel.purge(limit=100, check=lambda m: m.author == ctx.bot.user and (ctx.message.created_at - m.created_at).total_seconds() < time_limit)
        await ctx.send(f"Deleted {len(deleted)} bot messages.", delete_after=5)

    @commands.command(name="s")
    @commands.has_permissions(manage_messages=True)
    async def snipe(self, ctx):
        """Snipe the last deleted message."""
        # Implement your snipe functionality here
        pass

    @commands.command(name="cs")
    @commands.has_permissions(manage_messages=True)
    async def clear_snipe(self, ctx):
        """Clear the snipe history."""
        # Implement your clear snipe functionality here
        pass

    @commands.command(name="nuke")
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx):
        """Nukes the current channel with confirmation."""
        # Create the embed for confirmation
        embed = discord.Embed(
            title="Nuke Channel Confirmation",
            description="Are you sure you want to nuke this channel? Please reply with 'Yes' or 'No'.",
            color=discord.Color.red()
        )

        # Send the confirmation embed
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"]

        try:
            # Wait for the user's response
            response = await self.bot.wait_for('message', check=check, timeout=30.0)

            if response.content.lower() == 'yes':
                # Store original channel settings
                channel_name = ctx.channel.name
                category = ctx.channel.category
                overwrites = ctx.channel.overwrites

                # Delete the current channel
                await ctx.channel.delete()

                # Create a new channel with the same settings
                new_channel = await ctx.guild.create_text_channel(
                    name=channel_name,
                    category=category,
                    overwrites=overwrites,
                    topic=ctx.channel.topic,
                    reason="Channel nuked"
                )

                # Create a simplified message of users and roles with custom permissions
                custom_permissions = []
                for member, overwrite in overwrites.items():
                    if overwrite.is_empty():
                        continue  # Skip if no custom permissions
                    custom_permissions.append(f"{member.name}")  # Add user ID for clarity

                custom_permissions_message = "\n".join(custom_permissions) if custom_permissions else "No Custom Permissions"

                # Create the embed for the nuke message
                nuke_embed = discord.Embed(
                    title="Channel Nuked",
                    description=f"Channel nuked by {ctx.author.mention}",
                    color=discord.Color.red()
                )

                # Add fields for custom permissions and category
                nuke_embed.add_field(name="Settings Configured:", value=f"Permissions:\n{custom_permissions_message}\nCategory: {category.name if category else 'None'}", inline=False)

                # Send the embed to the new channel
                await new_channel.send(embed=nuke_embed)

                # Send "first" message in the new channel
                await new_channel.send("First 😭")

            else:
                await ctx.send("Nuke operation cancelled.")

        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Nuke operation cancelled.")

async def setup(bot):
    await bot.add_cog(Purge(bot))
