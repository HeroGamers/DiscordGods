import random

import discord
from discord import Embed
from discord.ext import commands

import database
from Util import logger


class GodManager(commands.Cog, name="Gods"):
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

    @commands.command(name="create", aliases=["newgod"])
    async def _create(self, ctx, *args):
        """Creates a new God"""
        user = ctx.author

        if database.isBeliever(user.id, ctx.guild.id):
            await ctx.send("You are already in a God, please leave it to create a new one using `/gods leave`!")
            return

        if database.godExists(args[0], ctx.guild.id):
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

    @commands.command(name="leave", aliases=["yeet"])
    async def _leave(self, ctx):
        """Leaves a God"""
        user = ctx.author

        if not database.isBeliever(user.id, ctx.guild.id):
            await ctx.send("You are not believing in a God!")
            return

        if database.leaveGod(user.id, ctx.guild.id):
            await ctx.send("You've left your god!")
        else:
            await ctx.send("Something went wrong...")

    @commands.command(name="join", aliases=["enter"])
    async def _join(self, ctx):
        """Joins a God"""
        user = ctx.author

        await ctx.send("yes")

    @commands.command(name="info", aliases=["godinfo"])
    async def _info(self, ctx, arg1):
        """Gets information about a God"""
        god = database.godExists(arg1, ctx.guild.id)

        if not god:
            await ctx.send("That God doesn't exist!")
            return

        embedcolor = discord.Color.green()
        if god.Type:
            for type, color in self.godtypes:
                if type == god.Type:
                    embedcolor = color

        if god.Description:
            embed = discord.Embed(title="God Information", color=embedcolor,
                                  description=god.Description)
        else:
            embed = discord.Embed(title="God Information", color=embedcolor)
        embed.add_field(name="Creation Date",
                        value="%s" % god.CreationDate.strftime(
                            "%Y-%m-%d %H:%M:%S"), inline=True)
        believers = database.getBelieversByID(god.ID)
        if not believers:
            believers = []
        embed.add_field(name="Believers", value="%s" % len(believers), inline=True)
        embed.set_footer(text="God Information for: %s" % god.Name,
                         icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GodManager(bot))
