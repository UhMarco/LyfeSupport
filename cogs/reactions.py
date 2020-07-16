import discord, platform, asyncio, os, time
from discord.ext import commands
from pathlib import Path
import utils.json

cwd = Path(__file__).parents[1]
cwd = str(cwd)

class Reactions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("- Reactions Cog loaded")

    @commands.command(aliases=['reactionrole', 'reactrole'])
    @commands.is_owner()
    async def rrs(self, ctx, messageid, emoji, role: discord.Role):
        message = await ctx.channel.fetch_message(messageid)

        if not message:
            await ctx.message.delete()
            return await ctx.send("RRs: Couldn't find message.", delete_after=3)

        data = utils.json.read_json("reactions")

        try:
            for i in range(len(data[str(messageid)])):
                broken = data[str(messageid)][i].split(';')
                if emoji == broken[0]:
                    await ctx.message.delete()
                    return await ctx.send(f"This emoji ({emoji}) is already being used in this message.", delete_after=3)
                elif str(role.id) == broken[1]:
                    await ctx.message.delete()
                    return await ctx.send(f"This role ({role.name}) is already being used in this message.", delete_after=3)
        except KeyError:
            pass

        try:
            await ctx.message.add_reaction(emoji)
            await ctx.message.delete()
        except discord.HTTPException:
            await ctx.message.delete()
            return await ctx.send("RRs: Invalid emoji used.", delete_after=3)

        await message.add_reaction(emoji)
        input = f"{emoji};{role.id}"
        data.setdefault(str(messageid), []).append(input)
        utils.json.write_json(data, "reactions")

    @rrs.error
    async def rrs_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Usage: `.rrs (message id) (emoji) (role)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("RRs: Couldn't find role.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        data = utils.json.read_json("reactions")

        guild = discord.utils.find(lambda g : g.id == payload.guild_id, self.bot.guilds)
        channel = self.bot.get_channel(payload.channel_id)
        user = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)

        if str(message.id) not in data.keys():
            return

        for i in range(len(data[str(message.id)])):
            broken = data[str(message.id)][i].split(';')
            role = guild.get_role(int(broken[1]))
            if str(payload.emoji) == broken[0]:
                try:
                    await user.add_roles(role)
                except discord.Forbidden:
                    await channel.send(f"No permissions to give {role.name} to {user.name}.")
                    await message.remove_reaction(payload.emoji, user)

        for reaction in message.reactions:
            if not reaction.me:
                await message.remove_reaction(reaction, user)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        data = utils.json.read_json("reactions")

        guild = discord.utils.find(lambda g : g.id == payload.guild_id, self.bot.guilds)
        channel = self.bot.get_channel(payload.channel_id)
        user = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)

        if str(message.id) not in data.keys():
            return

        for i in range(len(data[str(message.id)])):
            broken = data[str(message.id)][i].split(';')
            role = guild.get_role(int(broken[1]))
            if str(payload.emoji) == broken[0]:
                await user.remove_roles(role)

        utils.json.write_json(data, "reactions")

    @commands.command(aliases=['removerrs'])
    async def delrrs(self, ctx, messageid):
        data = utils.json.read_json("reactions")
        if messageid not in data.keys():
            return await ctx.send("This message doesn't have reaction roles set.")
        del data[messageid]
        await ctx.send("Removed reaction roles for that message.")
        utils.json.write_json(data, "reactions")

    @delrrs.error
    async def delrrs_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Usage: `.delrrs (message id)`")

    @commands.Cog.listener()
    async def on_messge_delete(self, message):
        data = utils.json.read_json("reactions")
        if message.id in data.keys():
            del data[message.id]
            print("Message deleted with reaction roles set. Deleting...")
            utils.json.write_json(data, "reactions")

    @commands.command(aliases=['inforrs'])
    async def irrs(self, ctx, messageid):
        data = utils.json.read_json("reactions")
        message = "\n"
        reactions = []

        if messageid not in data.keys():
            return await ctx.send("This message doesn't have reaction roles set.")

        for i in range(len(data[messageid])):
            broken = data[messageid][i].split(';')
            emoji = broken[0]
            role = ctx.guild.get_role(int(broken[1]))
            if not role:
                return await ctx.send(f"Ermmm we have a problem. I couldn't fine the role with the id {broken[1]}. You should probably ping my owner.")
            appendme = f"**Emoji:** {emoji} // **Role**: {role.name}"
            reactions.append(appendme)

        await ctx.send(message.join(reactions))

    @irrs.error
    async def irrs_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Usage: `.irrs (message id)`")



def setup(bot):
    bot.add_cog(Reactions(bot))
