import discord
from discord.ext import commands

import database
from Util import logger


class Info(commands.Cog, name="Information"):
    def __init__(self, bot):
        self.bot = bot
        self.godtypes = [("FROST", discord.Color.blue()),
                         ("LOVE", discord.Color.red()),
                         ("EVIL", discord.Color.darker_grey()),
                         ("SEA", discord.Color.dark_blue()),
                         ("MOON", discord.Color.light_grey()),
                         ("SUN", discord.Color.dark_orange()),
                         ("THUNDER", discord.Color.orange()),
                         ("PARTY", discord.Color.magenta()),
                         ("WAR", discord.Color.dark_red()),
                         ("WISDOM", discord.Color.dark_purple()),
                         ("NATURE", discord.Color.green())]

    # ------------ INFORMATION ------------ #

    @commands.command(name="info", aliases=["godinfo"])
    async def _info(self, ctx, *args):
        """Gets information about a God"""
        god = None
        if len(args) > 0:
            god = database.getGodName(args[0], ctx.guild.id)
        else:

            believer = database.getBeliever(ctx.author.id, ctx.guild.id)
            if believer:

                god = database.getGod(believer.God)

        if not god:
            await ctx.send("That God doesn't exist!")
            return

        embedcolor = discord.Color.green()
        if god.Type:
            for type, color in self.godtypes:
                if type == god.Type:
                    embedcolor = color

        title = god.Name + " - God of " + god.Type.capitalize()
        if god.Description:
            embed = discord.Embed(title=title, color=embedcolor,
                                  description=god.Description)
        else:
            embed = discord.Embed(title=title, color=embedcolor)
        embed.add_field(name="Creation Date",
                        value="%s" % god.CreationDate.strftime(
                            "%Y-%m-%d %H:%M:%S"), inline=True)
        believers = database.getBelieversByID(god.ID)
        if not believers:
            believers = []
        embed.add_field(name="Believers", value="%s" % len(believers), inline=True)
        embed.add_field(name="Power", value=god.Power, inline=True)
        if god.Priest:
            priest = self.bot.get_user(int(database.getBelieverByID(god.Priest).UserID))
            embed.set_footer(text="Priest: %s" % priest.name+"#"+priest.discriminator,
                             icon_url=priest.avatar_url)
        else:
            embed.set_footer(text="This God has no priest yet!",
                             icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="list", aliases=["gods"])
    async def _list(self, ctx):
        """Lists the top Gods on the server"""
        gods = database.getGods(ctx.guild.id)
        if not gods:
            await ctx.send("There are no Gods in " + ctx.guild.name + ", yet... `/gods create <name>`")
            return

        i = 1
        godlist = ""

        for god in gods:
            if i > 15:
                break

            believers = database.getBelieversByID(god.ID)
            if not believers:
                believers = 0
            else:
                believers = len(database.getBelieversByID(god.ID))
            godtext = str("[" + str(i) + "]  > #" + god.Name + "\n"
                          "         God of " + god.Type.capitalize() + "\n"
                          "         Power: " + god.Power + "\n"
                          "         Believers: " + str(believers) + "\n")
            godlist = godlist+godtext

            i += 1

        await ctx.send("**The Gods of " + ctx.guild.name + "**\n\n"
                       "```pl\n" + godlist + "```")

    # Function used to try and get users from arguments
    @classmethod
    async def getUser(cls, ctx, arg):
        if arg.startswith("<@") and arg.endswith(">"):
            userid = arg.replace("<@", "").replace(">", "").replace("!", "")  # fuck you nicknames
        else:
            userid = arg

        user = None
        try:
            user = await ctx.bot.fetch_user(userid)
        except Exception as e:
            logger.logDebug("User not found! ID method - %s" % e)
            try:
                user = discord.utils.get(ctx.message.guild.members, name=arg)
            except Exception as e:
                logger.logDebug("User not found! Name method - %s" % e)
        if user is not None:
            logger.logDebug("User found! - %s" % user.name)
            return user
        else:
            raise Exception("User not found!")

    @commands.command(name="marriages", aliases=["not_singles_like_you"])
    async def _marriages(self, ctx):
        """Lists the most loving married couples on the server"""
        marriages = database.getMarriages(ctx.guild.id)
        if not marriages:
            await ctx.send("There are no Marriages in " + ctx.guild.name + ", yet... `/gods marry <someone special>`")
            return

        i = 1
        marriagelist = ""

        for marriage in marriages:
            if i > 15:
                break

            believer1 = await self.getUser(ctx, database.getBelieverByID(marriage.Believer1).UserID)

            believer2 = await self.getUser(ctx, database.getBelieverByID(marriage.Believer2).UserID)

            god = database.getGod(marriage.God)

            marrytext = str("[" + str(i) + "]  > #" + believer1.name + " & " + believer2.name + "\n"
                            "         Loved: " + marriage.LoveDate.strftime("%Y-%m-%d %H:%M:%S") + "\n"
                            "         God: " + god.Name + "\n")
            marriagelist = marriagelist + marrytext

            i += 1

        await ctx.send("**The Married Couples of " + ctx.guild.name + "**\n\n"
                       "```pl\n" + marriagelist + "```")


def setup(bot):
    bot.add_cog(Info(bot))
