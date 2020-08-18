import discord
from discord.ext import commands
import database
from Util import logger
from Util.botutils import botutils


class BotManager(commands.Cog, name="Bot Commands"):
    def __init__(self, bot):
        """Where is the source code? How can I invite the bot? All these questions have their answers right here."""
        self.bot = bot

    @commands.command(name="howto", aliases=["helpme"])
    async def _howto(self, ctx, *args):
        """Get help on how to use Gods."""
        prefix = botutils.getPrefix(ctx.guild.id)
        if not args:
            await ctx.send("```\n"
                           "So... You want to start a new religion. Or, maybe you want to join an already existing "
                           "religion? Wait... oh, you are already experienced in the ways of Gods? Well, there are "
                           "categories to further expand your knowledge around this mess of commands!\n"
                           "\n"
                           "  <> = required argument. [] = optional argument.\n"
                           "\n"
                           "> Creating a new religion:\n"
                           "    " + prefix + "create <godName> [gender]   "
                                             "Create a new religion. Gender is optional.\n"
                           "> Joining an already created religion:\n"
                           "    " + prefix + "join <godName>              "
                                             "Joins a religion.\n"
                           "> Praying to your God:\n"
                           "    " + prefix + "pray                        "
                                             "Prays to a God, raising it's Power and Mood, and gaining Prayer Power.\n"
                           "\n"
                           "For more specialized help, use '" + prefix + "howto [category]'.\n"
                           "Categories:\n"
                           "  Management                          "
                           "Gets help about managing a God. Directed towards Priests.\n"
                           "  Misc                                "
                           "Miscellaneous things like marriage and hugs.\n"
                           "```")
        else:
            if args[0].lower() == "management":
                await ctx.send("```\n"
                               "Phew, the management of religions. These commands are for Priests only.\n"
                               "\n"
                               "  <> = required argument. [] = optional argument.\n"
                               "\n"
                               "> Set your religion to invite-only:\n"
                               "    " + prefix + "access                      "
                                                 "Set your religion as open or invite only.\n"
                               "> Change the description of your religion:\n"
                               "    " + prefix + "description <desc>          "
                                                 "Sets a description.\n"
                               "> Invite someone to your religion:\n"
                               "    " + prefix + "invite <mention or ID>      "
                                                 "Invites said user to your religion.\n"
                               "> Set the gender of your God:\n"
                               "    " + prefix + "setgender <gender>          "
                                                 "Changes the gender of your God. Examples include female and "
                                                 "sexless.\n"
                               "> Set the type of your God:\n"
                               "    " + prefix + "settype <type>              "
                                                 "Example types include Love, War and Thunder.\n"
                               "```")
            elif (args[0].lower() == "misc") or (args[0].lower() == "miscellaneous"):
                await ctx.send("```\n"
                               "So, you wanna get married, huh?\n"
                               "\n"
                               "  <> = required argument. [] = optional argument.\n"
                               "\n"
                               "> Marrying someone:\n"
                               "    " + prefix + "marry <mention or ID>       "
                                                 "Proposes to marry someone. The person you marry must believe in the "
                                                 "same religion as you.\n"
                               "> Loving/kissing your lover:\n"
                               "    " + prefix + "love                        "
                                                 "Kisses your special someone, bringing you to the top of the"
                                                 "marriage list. This costs no Prayer Power.\n"
                               "> Hug someone:\n"
                               "    " + prefix + "hug <mention or ID>         "
                                                 "Hugs someone - Costs 0.5 Prayer Power.\n"
                               "```")
            else:
                await ctx.send("Category not found!")

    @commands.command(name="source", aliases=["code", "sourcecode"])
    async def _source(self, ctx):
        """View and/or help with the source code of Gods."""
        await ctx.send("The source code for Gods can be found here: https://github.com/Fido2603/DiscordGods")

    @commands.command(name="support")
    async def _support(self, ctx):
        """Get help and support regarding the bot."""
        await ctx.send("The server where the Gods roam, Treeland: https://discord.gg/PvFPEfd")

    @commands.command(name="botinvite", aliases=["invitebot", "addbot"])
    async def _botinvite(self, ctx):
        """How to invite the bot."""
        await ctx.send(
            "Invite me to your server with this link: "
            "<https://discordapp.com/oauth2/authorize?scope=bot&client_id=180405652605239296>")

    @commands.command(name="botinfo", aliases=["bot"])
    async def _botinfo(self, ctx):
        """Retrives information about the bot."""
        embed = discord.Embed(title="Bot Information", color=discord.Color.green(),
                              description="")
        embed.add_field(name="Creation Date",
                        value="%s" % discord.utils.snowflake_time(ctx.bot.user.id).strftime(
                            "%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Guilds", value="%s" % len(self.bot.guilds), inline=True)
        embed.add_field(name="Gods", value="%s" % str(database.getGodsGlobalCount()), inline=True)
        embed.add_field(name="Believers", value="%s" % str(database.getBelieversGlobalCount()), inline=True)
        embed.add_field(name="Privacy Policy", value="For the Privacy Policy, please [click here](https://gist.github.com/HeroGamers/a92b824d899981c4c6c287978a54548c)!", inline=True)
        embed.set_footer(text="%s" % ctx.author.name,
                         icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="loadcog", aliases=["loadextension"])
    @commands.is_owner()
    async def _loadcog(self, ctx, arg1):
        """Loads a cog."""
        bot = self.bot
        try:
            bot.load_extension(f"cogs.{arg1}")
            await ctx.send(f"Successfully loaded the {arg1} extension")
            await logger.log("Moderator `%s` loaded the extension %s" % (ctx.author.name, arg1), bot, "INFO")
        except Exception as e:
            await ctx.send(f"Failed to load the extension {arg1}")
            await logger.log(f"Failed to load the extension {arg1} - {e}", bot, "ERROR")

    @commands.command(name="listcogs", aliases=["cogs"])
    @commands.is_owner()
    async def _listcogs(self, ctx):
        """Lists all the cogs."""
        embed = discord.Embed(title="Cogs", color=discord.Color.green(),
                              description="`AdminManager, BelieverManager, BotLists, BotManager, GodManager, Info, "
                                          "Misc, Tasks`")
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="unloadcog", aliases=["unloadextension"])
    @commands.is_owner()
    async def _unloadcog(self, ctx, arg1):
        """Unloads a cog."""
        bot = self.bot
        try:
            bot.unload_extension(f"cogs.{arg1}")
            await ctx.send(f"Successfully unloaded the {arg1} extension")
            await logger.log("Moderator `%s` unloaded the extension %s" % (ctx.author.name, arg1), bot, "INFO")
        except Exception as e:
            await ctx.send(f"Failed to unload the extension {arg1}")
            await logger.log(f"Failed to unload the extension {arg1} - {e}", bot, "ERROR")


def setup(bot):
    bot.add_cog(BotManager(bot))
