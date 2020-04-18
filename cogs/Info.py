import discord
from discord.ext import commands
import database
from Util.botutils import botutils


class Info(commands.Cog, name="Information"):
    def __init__(self, bot):
        self.bot = bot

    # ------------ INFORMATION ------------ #

    @commands.command(name="info", aliases=["godinfo", "i"])
    async def _info(self, ctx, *args):
        """Gets information about a God"""
        if len(args) > 0:
            god = database.getGodName(args[0], ctx.guild.id)
        else:
            believer = database.getBeliever(ctx.author.id, ctx.guild.id)
            if believer:
                god = database.getGod(believer.God)
            else:
                await ctx.send("Please give a God name!")
                return

        if not god:
            await ctx.send("That God doesn't exist!")
            return

        embedcolor = discord.Color.green()
        if god.Type:
            if god.Type.upper() == "YAOI":
                embedcolor = discord.Color.from_rgb(204, 235, 245)
            if god.Type.upper() == "TRAPS":
                embedcolor = discord.Color.from_rgb(248, 184, 248)
            for type, color in botutils.godtypes:
                if type == god.Type:
                    embedcolor = color

        title = god.Name + " - " + botutils.getGodString(god) + " of " + god.Type.capitalize()
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
        embed.add_field(name="Power", value=round(god.Power, 1), inline=True)
        if god.Gender:
            embed.add_field(name="Gender:", value=god.Gender.capitalize(), inline=True)
        embed.add_field(name="Mood:", value=botutils.getGodMood(god.Mood), inline=True)
        embed.add_field(name="Invite Only:", value=god.InviteOnly, inline=True)
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

        gods = list(gods)
        gods.reverse()

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
                          "         " + botutils.getGodString(god) + " of " + god.Type.capitalize() + "\n"
                          "         Power: " + str(round(god.Power, 2)) + "\n"
                          "         Believers: " + str(believers) + "\n")
            godlist = godlist+godtext

            i += 1

        await ctx.send("**The Gods of " + ctx.guild.name + "**\n\n"
                       "```pl\n" + godlist + "```")

    @commands.command(name="globallist", aliases=["globalgods", "glist", "ggods"])
    async def _globallist(self, ctx):
        """Lists the top Gods globally"""
        gods = database.getGodsGlobal()
        if not gods:
            await ctx.send("There are no Gods, yet... `/gods create <name>`")
            return

        gods = list(gods)
        gods.reverse()

        i = 1
        godlist = ""

        for god in gods:
            if i > 10:
                break

            believers = database.getBelieversByID(god.ID)
            if not believers:
                believers = 0
            else:
                believers = len(database.getBelieversByID(god.ID))

            guild_name = "NaN"

            guild = self.bot.get_guild(int(god.Guild))
            if guild:
                guild_name = guild.name

            godtext = str("[" + str(i) + "]  > #" + god.Name + "\n"
                          "         " + botutils.getGodString(god) + " of " + god.Type.capitalize() + "\n"
                          "         Power: " + str(round(god.Power, 2)) + "\n"
                          "         Believers: " + str(believers) + "\n"
                          "         Server: " + guild_name + "\n")
            godlist = godlist + godtext

            i += 1

        await ctx.send("**The Global Gods Leaderboard**\n\n"
                       "```pl\n" + godlist + "```")

    @commands.command(name="marriages", aliases=["not_singles_like_you", "marrylist"])
    async def _marriages(self, ctx):
        """Lists the most loving married couples on the server"""
        marriages = database.getMarriages(ctx.guild.id)
        if not marriages:
            await ctx.send("There are no Marriages in " + ctx.guild.name + ", yet... `/gods marry <someone special>`")
            return

        marriages = list(marriages)
        marriages.reverse()

        i = 1
        marriagelist = ""

        for marriage in marriages:
            if i > 15:
                break

            believer1 = await botutils.getUser(self.bot, ctx.guild, database.getBelieverByID(marriage.Believer1).UserID)

            believer2 = await botutils.getUser(self.bot, ctx.guild, database.getBelieverByID(marriage.Believer2).UserID)

            god = database.getGod(marriage.God)

            marrytext = str("[" + str(i) + "]  > #" + believer1.name + " & " + believer2.name + "\n"
                            "         Loved: " + marriage.LoveDate.strftime("%Y-%m-%d %H:%M:%S") + "\n"
                            "         " + botutils.getGodString(god) + ": " + god.Name + "\n")
            marriagelist = marriagelist + marrytext

            i += 1

        await ctx.send("**The Married Couples of " + ctx.guild.name + "**\n\n"
                       "```pl\n" + marriagelist + "```")

    @commands.command(name="globalmarriages", aliases=["gmarriages", "globalmarrylist"])
    async def _globalmarriages(self, ctx):
        """Lists the most loving married couples globally"""
        marriages = database.getMarriagesGlobal()
        if not marriages:
            await ctx.send("There are no Marriages, yet... `/gods marry <someone special>`")
            return

        marriages = list(marriages)
        marriages.reverse()

        i = 1
        marriagelist = ""

        for marriage in marriages:
            if i > 10:
                break

            believer1 = await botutils.getUser(self.bot, ctx.guild, database.getBelieverByID(marriage.Believer1).UserID)

            believer2 = await botutils.getUser(self.bot, ctx.guild, database.getBelieverByID(marriage.Believer2).UserID)

            god = database.getGod(marriage.God)
            guild_name = "NaN"

            guild = self.bot.get_guild(int(god.Guild))
            if guild:
                guild_name = guild.name

            marrytext = str("[" + str(i) + "]  > #" + believer1.name + " & " + believer2.name + "\n"
                            "         Loved: " + marriage.LoveDate.strftime("%Y-%m-%d %H:%M:%S") + "\n"
                            "         " + botutils.getGodString(god) + ": " + god.Name + "\n"
                            "         Server: " + guild_name + "\n")
            marriagelist = marriagelist + marrytext

            i += 1

        await ctx.send("**The Global Married Couples Leaderboard**\n\n"
                       "```pl\n" + marriagelist + "```")


def setup(bot):
    bot.add_cog(Info(bot))
