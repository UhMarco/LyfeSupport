import discord, platform, datetime, logging
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Support(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("- Support Cog loaded")

    @commands.command(aliases=['commands'])
    async def help(self, ctx):
        embed = discord.Embed(title=":herb: Lyfé Support Command List", color=discord.Color.red())
        embed.add_field(name=f"{self.bot.prefix}info", value="Get info about the channel you're in. This includes formats or procedures where applicable.", inline=False)
        embed.add_field(name=f"{self.bot.prefix}report (message)", value="Send a report directly to the developers. Although #error-report is preferred.", inline=False)
        embed.add_field(name=f"{self.bot.prefix}invite", value="Get the invite link to this server.", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['info'])
    async def channelinfo(self, ctx):
        channel = ctx.message.channel.name
        if channel == "general":
            embed = discord.Embed(title=f"#{channel}", description="This is the general channel that can be used for all sorts of conversation, preferably related to Lyfé or discord bots.", color=discord.Color.red())

        elif channel == "off-topic":
            embed = discord.Embed(title=f"#{channel}", description="This is a channel for any off-topic converssation as stated in the title and description. Any and all conversation is welcome.", color=discord.Color.red())

        elif channel == "bot-commands":
            embed = discord.Embed(title=f"#{channel}", description="This is the channel dedicated to bot commands. Spam is fine as long as it's not over-the-top. Those attempting to stress test bots will fail and also be punished.", color=discord.Color.red())

        elif channel == "lyfé-help":
            embed = discord.Embed(title=f"#{channel}", description="If you're unsure about anything relating to Lyfé Bot then this the channel to ask your questions. Please know that some information may be sensitive and staff are not required to answer some questions nor give reason for such decisions.", color=discord.Color.red())

        elif channel == "error-report":
            embed = discord.Embed(title=f"#{channel}", description="If you think you've found a bug or error with the bot, this is the place to report it.\nPlease describe in as detailed a manor as possible and screenshots are advised to be used.\n\n**Suggested Format:**\nCommand: `help`\nIssue: `does nothing`\nBot's response: `none`\n\n**Note:** If an error is not reproducible then it's likely impossible to fix.", color=discord.Color.red())

        else:
            embed = discord.Embed(title=f"#{channel}", description="No information found for this channel.", color=discord.Color.red())

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def report(self, ctx, *, message):
        owner = self.bot.get_user(259740408462966786)
        await owner.send(f"**{ctx.author}** reported: `{message}`")
        embed = discord.Embed(title=f'Report has been sent', description="Thank you for reporting!", color=discord.Color.red())
        await ctx.send(embed=embed)

    @report.error
    async def report_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"This command is used if you wish to report an error directly to the devs.\nUsage: `{self.bot.prefix}report (message)`")

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(description=":mailbox_with_mail: Invite others to the [Lyfe Support Server](https://discord.gg/zAZ3vKJ)", color=discord.Color.red())
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Support(bot))
