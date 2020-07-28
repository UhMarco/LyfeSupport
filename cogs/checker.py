import discord, platform, datetime, logging, asyncio
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

minute = 60

class Checker(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("- Checker Cog loaded")
        check_num = 0
        true_check = 0
        guild = self.bot.get_guild(733408726387654697)
        user = guild.get_member(730874220078170122)
        owner = guild.get_member(259740408462966786)
        while True:
            check_num += 1
            if user.status != discord.Status.online:
                true_check += 1
                msg = f"Bot offline! Check: {true_check}/{check_num}"
                await owner.send(msg)
                print(msg)

            await asyncio.sleep(minute * 15)

def setup(bot):
    bot.add_cog(Checker(bot))
