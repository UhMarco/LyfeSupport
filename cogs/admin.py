import discord, platform, datetime, logging, asyncio
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        data = utils.json.read_json("blacklist")
        for item in data["blacklistedUsers"]:
            self.bot.blacklisted_users.append(item)
        print("- Admin Cog loaded")

    @commands.command(aliases=['staffhelp', 'mhelp', 'shelp'])
    @commands.has_any_role("Moderator", "Support")
    async def modhelp(self, ctx):
        embed = discord.Embed(title=":herb: Staff Commands List", color=discord.Color.red())
        embed.add_field(name=f"{self.bot.prefix}purge (limit)", value="Group delete an amount of messages.", inline=False)
        embed.add_field(name=f"{self.bot.prefix}ban (user) [reason]", value="Ban a user from the server.", inline=False)
        embed.add_field(name=f"{self.bot.prefix}kick (user) [reason]", value="Kick a user from the server.", inline=False)
        embed.add_field(name=f"{self.bot.prefix}mute (user) [time] [reason]", value="Prevent a user from sending messages, reacting to messages or speaking in channels.", inline=False)
        embed.add_field(name=f"{self.bot.prefix}unmute (user)", value="Unmute a user.", inline=False)
        embed.add_field(name=f"{self.bot.prefix}blacklist (user)", value="Rarely used: Prevent someone from using bot commands.", inline=False)
        embed.add_field(name=f"{self.bot.prefix}unblacklist (user)", value="Rarely used: Allow someone to using bot commands again.", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role("Moderator", "Support")
    async def purge(self, ctx, amount: int):
        if not amount:
            await ctx.message.delete()
            return await ctx.author.send(f"Usage: `{self.bot.prefix}purge (limit)`")
        elif amount <= 250:
            await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f":wastebasket: Deleted {amount} messages.", delete_after=3)
        else:
            await ctx.message.delete()
            await ctx.author.send("Too much! The limit is 250.")

    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            await ctx.message.delete()
            await ctx.author.send(f"Usage: `{self.bot.prefix}purge (limit)`")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- BLACKLIST ----------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    @commands.has_any_role("Moderator", "Support")
    async def blacklist(self, ctx, member: discord.Member):
        if ctx.message.author.id == member.id:
            return await ctx.send("You can't blacklist yourself.")

        data = utils.json.read_json("blacklist")

        if member.id in data["blacklistedUsers"]:
            return await ctx.send("This user is already blacklisted.")

        data["blacklistedUsers"].append(member.id)
        self.bot.blacklisted_users.append(member.id)
        utils.json.write_json(data, "blacklist")
        await ctx.send(f"Blacklisted **{member.name}**.")
        print(f"{ctx.author.name} blacklisted {member.name}")

    # ----- ERROR HANDLER ------------------------------------------------------

    @blacklist.error
    async def blacklist_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}blacklist (user)`")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- UNBLACKLIST --------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    @commands.has_any_role("Moderator", "Support")
    async def unblacklist(self, ctx, member: discord.Member):
        data = utils.json.read_json("blacklist")

        if member.id not in data["blacklistedUsers"]:
            return await ctx.send("That user isn't blacklisted.")

        data["blacklistedUsers"].remove(member.id)
        self.bot.blacklisted_users.remove(member.id)
        utils.json.write_json(data, "blacklist")
        await ctx.send(f"Unblacklisted **{member.name}**.")
        print(f"{ctx.author.name} unblacklisted {member.name}")

    # ----- ERROR HANDLER ------------------------------------------------------

    @unblacklist.error
    async def unblacklist_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Usage: `.unblacklist (user)`")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- LOGOUT -------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['disconnect', 'stop', 's'])
    @commands.is_owner()
    async def logout(self, ctx):
        if self.bot.maintenancemode:
            return
        await ctx.send("Stopping.")
        await self.bot.logout()

    # ----- BASIC SERVER MODERATION --------------------------------------------

    @commands.command()
    @commands.has_any_role("Moderator", "Support")
    async def ban(self, ctx, user: discord.Member, *, reason="none provided"):
        if not user:
            return await ctx.send("Please specify a user.")

        if user == ctx.author:
            return await ctx.send("You cannot punish yourself.")

        try:
            await user.ban(reason=f"Banned by {ctx.author} for {reason}")
            await ctx.send(f"**{user}** banned for {reason}.")

        except discord.Forbidden:
            return await ctx.send("I couldn't ban that user.")

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}ban (user) [reason]`")


    # ----- KICKING -----
    @commands.command()
    @commands.has_any_role("Moderator", "Support")
    async def kick(self, ctx, user: discord.Member, *, reason="none provided"):
        if not user:
            return await ctx.send("Please specify a user.")

        if user == ctx.author:
            return await ctx.send("You cannot punish yourself.")

        try:
            await user.kick(reason=f"Kicked by {ctx.author} for {reason}")
            await ctx.send(f"**{user}** was kicked.")

        except discord.Forbidden:
            return await ctx.send("I couldn't kick that user.")

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}kick (user) [reason]`")

    # ----- MUTING -----

    @commands.command()
    @commands.has_any_role("Moderator", "Support")
    async def mute(self, ctx, user: discord.Member, duration=None, *, reason="none provided"):
        if not user:
            return await ctx.send("Please specify a user.")

        if user == ctx.author:
            return await ctx.send("You cannot punish yourself.")

        if user == self.bot.user:
            return await ctx.send("Very funny...")

        mutedrole = discord.utils.get(ctx.guild.roles, name='Muted')
        if mutedrole is None:
            return await ctx.send("Please set up a `Muted` role.")

        if mutedrole in user.roles:
            return await ctx.send("This user is already muted.")

        timeEndings = ('s', 'm', 'h', 'd')
        if duration != None and duration.endswith(timeEndings) and any(char.isdigit() for char in duration.strip("smhd")):
            try:
                await user.add_roles(mutedrole) # 60 secs in a minute 3600 in an hour 86400 in a day
            except discord.Forbidden:
                return await ctx.send("I couldn't mute that user.")

            if duration.endswith('s'): # SECONDS
                await ctx.send(f"**{user}** has been muted by {ctx.author} for {duration.strip('s')} second(s).")
                await asyncio.sleep(int(duration.strip('s')))
                await user.remove_roles(mutedrole)

            elif duration.endswith('m'): # MINUTES
                await ctx.send(f"**{user}** has been muted by {ctx.author} for {duration.strip('m')} minute(s).")
                await asyncio.sleep(int(duration.strip('m')) * 60)
                await user.remove_roles(mutedrole)

            elif duration.endswith('h'): # HOURS
                await ctx.send(f"**{user}** has been muted by {ctx.author} for {duration.strip('h')} hour(s).")
                await asyncio.sleep(int(duration.strip('h')) * 3600)
                await user.remove_roles(mutedrole)

            elif duration.endswith('d'): # DAYS
                await ctx.send(f"**{user}** has been muted by {ctx.author} for {duration.strip('d')} day(s).")
                await asyncio.sleep(int(duration.strip('d')) * 86400)
                await user.remove_roles(mutedrole)

            return

        try:
            await user.add_roles(mutedrole)
        except discord.Forbidden:
            return await ctx.send("I couldn't mute that user.")

        await ctx.send(f"**{user}** has been muted indefinitley.")

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}mute (user) [reason]`")

    @commands.command()
    @commands.has_any_role("Moderator", "Support")
    async def unmute(self, ctx, user: discord.Member):
        if not user:
            return await ctx.send("Please specify a user.")

        mutedrole = discord.utils.get(ctx.guild.roles, name='Muted')

        if mutedrole not in user.roles:
            return await ctx.send("This user is not muted.")

        if mutedrole in user.roles:
            await user.remove_roles(mutedrole)
            await ctx.send(f"**{user}** has been unmuted.")

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}unmute (user) [reason]`")

def setup(bot):
    bot.add_cog(Admin(bot))
