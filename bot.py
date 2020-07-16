import discord, json, platform, logging, os, time
from discord.ext import commands
from pathlib import Path

import utils.json

cwd = Path(__file__).parents[0]
cwd = str(cwd)

prefix = '-'

bot = commands.Bot(command_prefix=prefix, case_insensitive=True, owner_id=259740408462966786)

bot.remove_command("help")

secret_file = json.load(open(cwd+"/bot_config/secrets.json"))
bot.config_token = secret_file["token"]
bot.prefix = prefix
bot.blacklisted_users = []
bot.upsince = time.time()
bot.maintenancemode = False
bot.loggingChannel = None

@bot.event
async def on_ready():
    print(f"-----\n{bot.user.name} Online\n-----\nPrefix: {bot.prefix}\n-----")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"out for {bot.prefix}help"), status=discord.Status.do_not_disturb)


@bot.event
async def on_message(message):
    # Ignore bot
    if message.author.id == bot.user.id:
        return

    # Blacklist system
    if message.author.id in bot.blacklisted_users:
        return

    # Auto responses go here

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)} ms")

@bot.command(aliases=['stats', 'status'])
@commands.is_owner()
async def extensions(ctx):
    modules = []
    message = "\n"
    count = 0

    for file in os.listdir(cwd+"/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            try:
                bot.load_extension(f"cogs.{file[:-3]}")
                bot.unload_extension(f"cogs.{file[:-3]}")
            except commands.ExtensionAlreadyLoaded:
                name = file[:-3]
                name = f"`✔ {name[:1].upper()}{name[1:]}`"
                modules.append(name)
                count += 1

            try:
                bot.unload_extension(f"cogs.{file[:-3]}")
                bot.load_extension(f"cogs.{file[:-3]}")
            except commands.ExtensionNotLoaded:
                name = file[:-3]
                name = f"`✘ {name[:1].upper()}{name[1:]}`"
                modules.append(name)

    m, s = divmod(time.time() - bot.upsince, 60)
    h, m = divmod(m, 60)
    if int(h) == 0 and int(m) == 0:
        uptime = f"{int(s)} seconds"
    elif int(h) == 0 and int(m) != 0:
        uptime = f"{int(m)} minutes and {int(s)} seconds"
    else:
        uptime = f"{int(h)} hours, {int(m)} minutes and {int(s)} seconds"

    await ctx.send(f"**Extensions:** `({count})`\n{message.join(modules)}\n**Latency:** `{round(bot.latency * 1000)} ms`\n**Uptime:** `{uptime}`")

if __name__ == '__main__':
    for file in os.listdir(cwd+"/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

bot.run(bot.config_token)
