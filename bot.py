# Import the config
try:
    import config
except ImportError:
    print("Couldn't import config.py! Exiting!")
    exit()

import asyncio
import discord
from discord.ext.commands._types import BotT
from Util import logger
from Util.botutils import botutils
import database
import os
from typing import Any
import cogs

# Import a monkey patch, if that exists
try:
    import monkeyPatch
except ImportError:
    print("DEBUG: No Monkey patch found!")

TEST_GUILD = discord.Object(id=473953130371874826)


class DiscordGods(discord.ext.commands.Bot):
    def __init__(self, command_prefix: discord.ext.commands.bot.PrefixType[BotT], *, intents: discord.Intents,
                 **options: Any) -> None:
        super().__init__(command_prefix=command_prefix, intents=intents, options=options)

    async def setup_hook(self):
        bot.remove_command("help")
        # Load commands
        for command_group in command_groups:
            try:
                bot.tree.add_command(command_group)
            except Exception as e:
                logger.logDebug(f"Failed to load command group {command_group}. - {e}", "ERROR")
        # Load tasks
        for task in tasks:
            try:
                await bot.load_extension(f"{task}")
            except Exception as e:
                logger.logDebug(f"Failed to load task {task}. - {e}", "ERROR")

        # TODO: change from test guild commands to global commands
        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)


intents = discord.Intents.default()
bot: discord.ext.commands.Bot = DiscordGods(intents=intents, description='Religion has never been easier!',
                                            command_prefix=os.getenv("prefix"),
                                            activity=discord.Game(name="with religions | /gods howto"))


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


# @bot.event
# async def on_command_error(ctx: commands.Context, error):
#     if isinstance(error, commands.NoPrivateMessage):
#         await ctx.send("This command cannot be used in private messages")
#     elif isinstance(error, commands.BotMissingPermissions):
#         await ctx.send(
#             embed=Embed(color=discord.Color.red(), description="I need permissions to do that!"))
#     elif isinstance(error, commands.MissingPermissions):
#         await ctx.send(
#             embed=Embed(color=discord.Color.red(), description="You are missing permissions to do that!"))
#     elif isinstance(error, commands.CheckFailure):
#         return
#     elif isinstance(error, commands.CommandOnCooldown):
#         return
#     elif isinstance(error, commands.MissingRequiredArgument):
#         return
#     elif isinstance(error, commands.BadArgument):
#         return
#     elif isinstance(error, commands.CommandNotFound):
#         return
#     elif "User not found!" in str(error):
#         await ctx.send("Error: User not found! Try mentioning or using an ID!")
#     else:
#         await ctx.send("Something went wrong while executing that command... Sorry!")
#         await logger.log("%s" % error, bot, "ERROR")


@bot.event
async def on_guild_join(guild: discord.Guild):
    await logger.log("Joined a new guild (`%s` - `%s`)" % (guild.name, guild.id), bot, "INFO")


@bot.event
async def on_guild_remove(guild: discord.Guild):
    await logger.log("Left a new guild (`%s` - `%s`)" % (guild.name, guild.id), bot, "INFO")

    # Disband any gods in the guild
    gods = database.getGods(guild.id)
    if gods:
        for god in gods:
            botutils.disbandGod(god.ID)


# @bot.event
# async def on_message(message: discord.Message):
#     if message.author.bot:
#         return
#     ctx: commands.Context = await bot.get_context(message)
#
#     if ctx.command is not None:
#         if isinstance(message.channel, discord.DMChannel):
#             await logger.log("`%s` (%s) used the `%s` command in their DM's" % (
#                 ctx.author.name, ctx.author.id, ctx.invoked_with), bot, "INFO")
#         else:
#             await logger.log("`%s` (%s) used the `%s` command in the guild `%s` (%s), in the channel `%s` (%s)" % (
#                 ctx.author.name, ctx.author.id, ctx.invoked_with, ctx.guild.name, ctx.guild.id, ctx.channel.name,
#                 ctx.channel.id), bot, "INFO")
#         await bot.invoke(ctx)

command_groups = [
    cogs.BotManager.BotManager(bot),
    cogs.GodManager.GodManager(bot),
    cogs.BelieverManager.BelieverManager(bot),
    cogs.Info.Info(bot),
    cogs.Misc.Misc(bot),
    cogs.AdminManager.AdminManager(bot)
]

tasks = [
    cogs.BotLists.BotLists(bot),
    cogs.Tasks.Tasks(bot)
]


async def main():
    logger.setup_logger()

    async with bot:
        await bot.start(os.getenv('token'))


if __name__ == '__main__':
    asyncio.run(main())
