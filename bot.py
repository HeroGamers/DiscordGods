# Import the config
try:
    import config
except ImportError:
    print("Couldn't import config.py! Exiting!")
    exit()

import discord
from discord.ext import commands
from discord import Embed
from Util import logger
from Util.botutils import botutils
import database
import os

# Import a monkey patch, if that exists
try:
    import monkeyPatch
except ImportError:
    print("DEBUG: No Monkey patch found!")


async def getPrefix(bot, message):
    guild = message.guild

    prefixes = [os.getenv('prefix')+"gods ", os.getenv('prefix')+"g ", "<@"+str(bot.user.id)+"> ", "<@!"+str(bot.user.id)+"> "]

    if guild:
        guildconfig = database.getGuild(guild.id)
        if guildconfig:
            prefixes.append(guildconfig.Prefix)
    return prefixes


bot = commands.Bot(command_prefix=getPrefix, description='Religion has never been easier!',
                   activity=discord.Game(name="...starting up!"))


startup_extensions = ["BotManager",
                      "GodManager",
                      "BotLists",
                      "BelieverManager",
                      "Info",
                      "Tasks",
                      "Misc",
                      "AdminManager"]


@bot.event
async def on_connect():
    logger.logDebug("----------[LOGIN SUCESSFULL]----------", "INFO")
    logger.logDebug("     Username: " + bot.user.name, "INFO")
    logger.logDebug("     UserID:   " + str(bot.user.id), "INFO")
    logger.logDebug("--------------------------------------", "INFO")
    print("\n")

    # Bot done starting up
    logger.logDebug("Bot startup done!\n", "INFO")


@bot.event
async def on_ready():
    # Bot startup is now done...
    logger.logDebug("Gods has (re)connected to Discord!")


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command cannot be used in private messages")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(
            embed=Embed(color=discord.Color.red(), description="I need permissions to do that!"))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            embed=Embed(color=discord.Color.red(), description="You are missing permissions to do that!"))
    elif isinstance(error, commands.CheckFailure):
        return
    elif isinstance(error, commands.CommandOnCooldown):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        return
    elif isinstance(error, commands.BadArgument):
        return
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        await ctx.send("Something went wrong while executing that command... Sorry!")
        await logger.log("%s" % error, bot, "ERROR")


@bot.event
async def on_guild_join(guild):
    await logger.log("Joined a new guild (`%s` - `%s`)" % (guild.name, guild.id), bot, "INFO")


@bot.event
async def on_guild_remove(guild):
    await logger.log("Left a new guild (`%s` - `%s`)" % (guild.name, guild.id), bot, "INFO")

    # Disband any gods in the guild
    gods = database.getGods(guild.id)
    if gods:
        for god in gods:
            botutils.disbandGod(god.ID)


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    ctx: commands.Context = await bot.get_context(message)

    if ctx.command is not None:
        if isinstance(message.channel, discord.DMChannel):
            await logger.log("`%s` (%s) used the `%s` command in their DM's" % (
                ctx.author.name, ctx.author.id, ctx.invoked_with), bot, "INFO")
        else:
            await logger.log("`%s` (%s) used the `%s` command in the guild `%s` (%s), in the channel `%s` (%s)" % (
                ctx.author.name, ctx.author.id, ctx.invoked_with, ctx.guild.name, ctx.guild.id, ctx.channel.name,
                ctx.channel.id), bot, "INFO")
        await bot.invoke(ctx)


if __name__ == '__main__':
    logger.setup_logger()

    # Load extensions
    for extension in startup_extensions:
        try:
            bot.load_extension(f"cogs.{extension}")
        except Exception as e:
            logger.logDebug(f"Failed to load extension {extension}. - {e}", "ERROR")

bot.run(os.getenv('token'))
