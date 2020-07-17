import discord, random, datetime
from discord.ext import commands

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("- Events Cog loaded")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(ctx.guild.roles, name='Member')
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignored errors
        ignored = (commands.CommandNotFound, commands.MissingRequiredArgument)#, commands.UserInputError commands.BadArgument
        if isinstance(error, ignored):
            return

        # Error handling
        if isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f':stopwatch: You must wait **{int(s)} seconds** to use this command again.')
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(f':stopwatch: You must wait **{int(m)} minutes and {int(s)} seconds** to use this command again.')
            else:
                await ctx.send(f':stopwatch: You must wait **{int(h)} hours, {int(m)} minutes and {int(s)} seconds** to use this command again.')
            return

        elif isinstance(error, commands.CheckFailure):
            return await ctx.send("Insufficient permissions.")

        elif isinstance(error, commands.CommandInvokeError):
            if str(error.original) == "403 Forbidden (error code: 50013): Missing Permissions":
                print("===== Attempting to handle in ctx =====")
                try:
                    embed = discord.Embed(title=":x: Missing Permissions", color=discord.Color.red())
                    await ctx.send(embed=embed)
                    return print("Success")
                except Exception:
                    print("Failed")

        print("\n----------\n")
        raise error
        print("\n----------\n")

def setup(bot):
    bot.add_cog(Events(bot))
