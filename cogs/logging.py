import discord, platform, asyncio, datetime
from discord.ext import commands
from pathlib import Path
import utils.json

cwd = Path(__file__).parents[1]
cwd = str(cwd)

class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("- Logging Cog loaded")
        self.bot.loggingChannel = self.bot.get_channel(utils.json.read_json("logging"))

    @commands.command(aliases=['logchannel', 'loggingchannel', 'setuplogging'])
    @commands.is_owner()
    async def logging(self, ctx, channel: discord.TextChannel=None):
        if channel is None:
            try:
                self.bot.loggingChannel = self.bot.get_channel(utils.json.read_json("logging"))
                return await ctx.send(f"Logging channel is set to {self.bot.loggingChannel.mention}")
            except Exception:
                return await ctx.send("There is currently no logging channel set")
        self.bot.loggingChannel = channel
        utils.json.write_json(channel.id, "logging")
        await ctx.send(f"Logging channel set to {channel.mention}")

    @logging.error
    async def logging_error(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("That's not a valid channel")


    @commands.Cog.listener()
    async def on_member_join(self, member):
        created = list(str(datetime.datetime.utcnow() - member.created_at)[:-7])

        x = 0
        for char in created:
            if char == ':':
                created[x] = " hours, "
                break
            x += 1

        x = 0
        for char in created:
            if char == ':':
                created[x] = " minutes and "
                break
            x += 1

        created = "".join(created)

        embed = discord.Embed(
            title="Member joined",
            color=discord.Colour.green(),
            description=f"{member.mention} joined the server.\nCreated {created} seconds ago.",
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name=member, icon_url=member.avatar_url)
        embed.set_footer(text=f"ID: {member.id}")
        if self.bot.loggingChannel == None:
            return print("Logging channel isn't set up!")
        await self.bot.loggingChannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        joined = list(str(datetime.datetime.utcnow() - member.joined_at)[:-7])

        x = 0
        for char in joined:
            if char == ':':
                joined[x] = " hours, "
                break
            x += 1

        x = 0
        for char in joined:
            if char == ':':
                joined[x] = " minutes and "
                break
            x += 1

        joined = "".join(joined)

        embed = discord.Embed(
            title="Member left",
            color=discord.Colour.red(),
            description=f"{member.mention} left the server.\nJoined {joined} seconds ago.",
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name=member, icon_url=member.avatar_url)
        embed.set_footer(text=f"ID: {member.id}")
        if self.bot.loggingChannel == None:
            return print("Logging channel isn't set up!")
        await self.bot.loggingChannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.content.startswith(self.bot.prefix):
            return
        if message.author != self.bot.user:
            embed = discord.Embed(
                title=f"Message deleted in #{message.channel.name}",
                color=discord.Colour.red(),
                description=message.content,
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            embed.set_footer(text=f"ID: {message.author.id}")
            if self.bot.loggingChannel == None:
                return print("Logging channel isn't set up!")
            await self.bot.loggingChannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, message):
        if before.author != self.bot.user and before.content != message.content:
            embed = discord.Embed(
                title=f"Message edited in #{message.channel.name}",
                color=discord.Colour.blue(),
                description=f"**Before:** {before.content}\n**After:** {message.content}",
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            embed.set_footer(text=f"ID: {message.author.id}")
            if self.bot.loggingChannel == None:
                return print("Logging channel isn't set up!")
            await self.bot.loggingChannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == None:
            embed = discord.Embed(
                title="Member joined voice channel",
                description=f"**{member}** joined `#{after.channel.name}`",
                color=discord.Colour.green(),
                timestamp=datetime.datetime.utcnow()
            )
        elif after.channel == None:
            embed = discord.Embed(
                title="Member left voice channel",
                description=f"**{member}** left `#{before.channel.name}`",
                color=discord.Colour.red(),
                timestamp=datetime.datetime.utcnow()
            )
        elif before.channel != after.channel:
            embed = discord.Embed(
                title="Member switched voice channel",
                description=f"**{member}** switched `#{before.channel.name}` --> `#{after.channel.name}`",
                color=discord.Colour.blue(),
                timestamp=datetime.datetime.utcnow()
            )
        elif after.self_stream:
            embed = discord.Embed(
                title="Member started streaming",
                description=f"**{member}** started streaming in `#{before.channel.name}`",
                color=discord.Colour.purple(),
                timestamp=datetime.datetime.utcnow()
            )
        elif before.self_stream and after.self_stream == False:
            embed = discord.Embed(
                title="Member stopped streaming",
                description=f"**{member}** stopped streaming in `#{before.channel.name}`",
                color=discord.Colour.purple(),
                timestamp=datetime.datetime.utcnow()
            )
        else:
            return
        embed.set_author(name=member, icon_url=member.avatar_url)
        embed.set_footer(text=f"ID: {member.id}")
        if self.bot.loggingChannel == None:
            return print("Logging channel isn't set up!")
        await self.bot.loggingChannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        member = after
        if before.nick != after.nick:
            embed = discord.Embed(
                title="Member updated nickname",
                color=discord.Colour.blue(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="Before:", value=before.nick)
            embed.add_field(name="After:", value=after.nick)

        elif before.roles != after.roles:
            add = list(set(after.roles) - set(before.roles))
            rem = list(set(before.roles) - set(after.roles))
            try:
                if add[0] in after.roles:
                    embed = discord.Embed(
                        title="Member updated roles",
                        color=discord.Colour.blue(),
                        timestamp=datetime.datetime.utcnow(),
                        description=f"Added `{add[0].name}` role"
                    )
            except IndexError:
                try:
                    if rem[0] in before.roles:
                        embed = discord.Embed(
                            title="Member updated roles",
                            color=discord.Colour.blue(),
                            timestamp=datetime.datetime.utcnow(),
                            description=f"Removed `{rem[0].name}` role"
                        )
                except IndexError:
                    return
        else:
            return

        embed.set_author(name=member, icon_url=member.avatar_url)
        embed.set_footer(text=f"ID: {member.id}")
        if self.bot.loggingChannel == None:
            return print("Logging channel isn't set up!")
        await self.bot.loggingChannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        member = after
        if before.avatar != after.avatar:
            embed = discord.Embed(
                title="Member updated avatar",
                description=after.mention,
                color=discord.Colour.blue(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=after.avatar_url)
            embed.set_author(name=member, icon_url=member.avatar_url)
            embed.set_footer(text=f"ID: {member.id}")
            if self.bot.loggingChannel == None:
                return print("Logging channel isn't set up!")
            await self.bot.loggingChannel.send(embed=embed)

        if before.name != after.name:
            embed = discord.Embed(
                title="Member updated name",
                description=f"**Before:** {before.name}\n**After:** {after.name}",
                color=discord.Colour.blue(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_author(name=member, icon_url=member.avatar_url)
            embed.set_footer(text=f"ID: {member.id}")
            if self.bot.loggingChannel == None:
                return print("Logging channel isn't set up!")
            await self.bot.loggingChannel.send(embed=embed)

        if before.discriminator != after.discriminator:
            embed = discord.Embed(
                title="Member updated discriminator",
                description=f"**Before:** #{before.discriminator}\n**After:** #{after.discriminator}",
                color=discord.Colour.blue(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_author(name=member, icon_url=member.avatar_url)
            embed.set_footer(text=f"ID: {member.id}")
            if self.bot.loggingChannel == None:
                return print("Logging channel isn't set up!")
            await self.bot.loggingChannel.send(embed=embed)

def setup(bot):
    bot.add_cog(Logging(bot))
