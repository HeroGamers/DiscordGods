import random
import discord
from discord.ext import commands
import database
from Util import logger


class GodManager(commands.Cog, name="Religion Management"):
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

    # ------------ GOD MANAGEMENT ------------ #

    @commands.command(name="create", aliases=["newgod"])
    async def _create(self, ctx, *args):
        """Creates a new God"""
        user = ctx.author

        if database.getBeliever(user.id, ctx.guild.id):
            await ctx.send("You are already in a God, please leave it to create a new one using `/gods leave`!")
            return

        if database.getGodName(args[0], ctx.guild.id):
            await ctx.send("A God with that name already exists!")
            return

        if len(args) > 1:
            god = database.newGod(ctx.guild.id, args[0], random.choice(self.godtypes)[0], args[1])
        else:
            god = database.newGod(ctx.guild.id, args[0], random.choice(self.godtypes)[0])
        if god.ID:
            await ctx.send("God created!")
            believer = database.newBeliever(user.id, god)
            if believer.ID:
                logger.logDebug("Believer created!")
        else:
            await ctx.send("Boohoo, God creation failed...")

    @classmethod
    async def isBelieverAndPriest(cls, ctx):
        believer = database.getBeliever(ctx.author.id, ctx.guild.id)
        if not believer:
            await ctx.send("You are not believing in a God!")
            return False

        god = database.getGod(believer.God)
        if not god.Priest or god.Priest != believer.ID:
            await ctx.send("You are not a priest!")
            return False

        return god

    @commands.command(name="access", aliases=["lock", "open"])
    async def _access(self, ctx):
        """Set your religion as open or invite only"""
        god = await self.isBelieverAndPriest(ctx)

        if god:
            if database.toggleAccess(god.ID):
                await ctx.send("God is now Invite Only!")
            else:
                await ctx.send("God is now Open!")

    @commands.command(name="ally", aliases=["friend"])
    async def _ally(self, ctx):
        """Toggles alliance with another religion - Not done"""
        logger.logDebug("yes")

    @commands.command(name="war", aliases=["enemy"])
    async def _war(self, ctx):
        """Toggles war with another religion - Not done"""
        logger.logDebug("yes")

    @commands.command(name="description", aliases=["desc"])
    async def _description(self, ctx, *args):
        """Sets a description for your religion"""
        god = await self.isBelieverAndPriest(ctx)

        if god:
            desc = ""
            for arg in args:
                desc = desc + " " + arg
            desc.strip()

            if len(desc) > 100:
                await ctx.send("Keep your description under 100 chars, please.")
                return

            database.setDesc(god.ID, desc)
            await ctx.send("Description set successfully!")

    @commands.command(name="invite", aliases=["inv"])
    async def _invite(self, ctx):
        """Invite someone to your religion - Not done"""
        logger.logDebug("yes")


def setup(bot):
    bot.add_cog(GodManager(bot))
