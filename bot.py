import discord
from discord.ext import commands
from discord import Embed, Permissions
from Util import logger
import os
import database

# Import the config
try:
    import config
except ImportError:
    print("Couldn't import config.py! Exiting!")
    exit()

# Import a monkey patch, if that exists
try:
    import monkeyPatch
except ImportError:
    print("DEBUG: No Monkey patch found!")


bot = commands.Bot(command_prefix=(os.getenv('prefix')+"gods ", os.getenv('prefix')+"g "),
                   description='Religion has never been easier!',
                   activity=discord.Game(name="with " + str(len(database.getBelieversGlobal())) + " believers | " + os.getenv('prefix') + "gods help"))


startup_extensions = ["BotManager",
                      "GodManager",
                      "BelieverManager",
                      "Info"]


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
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    ctx: commands.Context = await bot.get_context(message)
    if message.content.startswith(os.getenv('prefix')+"gods ") or message.content.startswith(os.getenv('prefix')+"g "):
        if ctx.command is not None:
            if isinstance(message.channel, discord.DMChannel):
                await logger.log("`%s` (%s) used the `%s` command in their DM's" % (
                    ctx.author.name, ctx.author.id, ctx.invoked_with), bot, "INFO")
            else:
                await logger.log("`%s` (%s) used the `%s` command in the guild `%s` (%s), in the channel `%s` (%s)" % (
                    ctx.author.name, ctx.author.id, ctx.invoked_with, ctx.guild.name, ctx.guild.id, ctx.channel.name,
                    ctx.channel.id), bot, "INFO")
            await bot.invoke(ctx)
    else:
        return


if __name__ == '__main__':
    logger.setup_logger()

    # Load extensions
    for extension in startup_extensions:
        try:
            bot.load_extension(f"cogs.{extension}")
        except Exception as e:
            logger.logDebug(f"Failed to load extension {extension}. - {e}", "ERROR")

bot.run(os.getenv('token'))
