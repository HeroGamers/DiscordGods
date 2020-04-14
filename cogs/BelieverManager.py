import asyncio
import datetime

import discord
from discord.ext import commands
import database
from Util import logger


class BelieverManager(commands.Cog, name="Believer"):
    def __init__(self, bot):
        self.bot = bot

    # ------------ BELIEVER INTERACTIONS WITH A RELIGION/GOD ------------ #

    @commands.command(name="leave", aliases=["yeet"])
    async def _leave(self, ctx):
        """Leaves a religion"""
        user = ctx.author

        believer = database.getBeliever(user.id, ctx.guild.id)
        if not believer:
            await ctx.send("You are not believing in a God!")
            return

        if database.leaveGod(user.id, ctx.guild.id):
            await ctx.send("You've left your god!")

            # If there aren't any believers in the God anymore, disband it
            if not database.getBelieversByID(believer.God):
                database.disbandGod(believer.God)

            # If the user was married, divorce them
            marriage = database.getMarriage(believer.ID, ctx.guild.id)
            if marriage:
                database.deleteMarriage(marriage.ID)
        else:
            await ctx.send("Something went wrong...")

    @commands.command(name="join", aliases=["enter"])
    async def _join(self, ctx, arg1):
        """Joins a religion"""
        believer = database.getBeliever(ctx.author.id, ctx.guild.id)
        if believer:
            await ctx.send("You are already in a God, please leave it to join a new one using `/gods leave`!")
            return

        god = database.getGodName(arg1, ctx.guild.id)
        if not god:
            await ctx.send("There is no God by that name... yet! `/gods create <name>`")
            return

        if god.InviteOnly:
            await ctx.send("That God is invite-only, and you don't have an invite...\n"
                           "Try contacting the Preist of the God for an invite!")
            return

        database.newBeliever(ctx.author.id, god.ID)
        await ctx.send("You've now become a believer in the name of " + god.Name + "!")

    @commands.command(name="no", aliases=["deny", "decline"])
    async def _no(self, ctx):
        """Reject a proposal from your God - Not done"""
        logger.logDebug("yes")

    @commands.command(name="yes", aliases=["accept"])
    async def _yes(self, ctx):
        """Accept a proposal from your God - Not done"""
        logger.logDebug("yes")

    @commands.command(name="pray", aliases=["p"])
    async def _pray(self, ctx):
        """Pray to your God - Not done"""
        believer = database.getBeliever(ctx.author.id, ctx.guild.id)
        if not believer:
            await ctx.send("You are not believing in any God, yet! `/gods create <name>`!")
            return

        date = datetime.datetime.now()
        timediff = date - believer.PrayDate
        minutes = timediff.total_seconds()/60

        if minutes >= 30:
            print(0)
            database.pray(believer.ID)
            believer = database.getBelieverByID(believer.ID)
            print(1)

            await ctx.send("You prayed to your God! Your prayer power is now **" + believer.PrayerPower + "**!")
        else:
            timeTillPray = 30-minutes
            await ctx.send("You cannot pray to your God yet! Time remaining: " + str(round(timeTillPray,1)) + " minutes.")

    # ------------ BELIEVER RELATIONSHIPS ------------ #

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

    @commands.command(name="marry", aliases=["propose"])
    async def _marry(self, ctx, arg1):
        """Marry that special someone"""
        guildid = ctx.guild.id
        user1 = ctx.author
        user2 = await self.getUser(ctx, arg1)

        believer1 = database.getBeliever(user1.id, guildid)
        believer2 = database.getBeliever(user2.id, guildid)

        if not believer1:
            await ctx.send("You are not believing in any religion!")
        elif database.getMarriage(believer1.ID, guildid):
            await ctx.send("You are already married?! What are you trying to do?! - Maybe you should look at getting a divorce... `/g divorce`")
        elif not believer2:
            await ctx.send("Your special someone is not believing in any religion!")
        elif database.getMarriage(believer2.ID, guildid):
            await ctx.send("Aww... Your special someone is already married...")
        elif believer1.God != believer2.God:
            await ctx.send("You are not believing in the same God as your special someone!")
        else:
            message = await ctx.send("<@" + str(user2.id) + "> " + user1.name + " wishes to marry you! Do you accept "
                                     "their proposal, to have and to hold each other, from this day forward, for "
                                     "better, for worse, for richer, for poorer, in sickness and in health, until "
                                     "death do you apart?")
            await message.add_reaction('👍')

            def check_for_react(reaction, user):
                return user == user2 and str(reaction.emoji) == '👍' and reaction.message.id == message.id

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_for_react)
            except asyncio.TimeoutError:
                await ctx.send("Awh, too slow!")
            else:
                database.newMarriage(believer1.ID, believer2.ID, believer1.God)
                await ctx.send("<@" + str(user1.id) + "> and <@" + str(user2.id) + "> are now married in the name of " +
                               database.getGod(believer1.God).Name + "!")

    @commands.command(name="divorce", aliases=["leave_with_the_kids"])
    async def _divorce(self, ctx):
        """Leave your special someone and take the kids with you - Not done"""
        logger.logDebug("yes")

    @commands.command(name="love", aliases=["kiss"])
    async def _love(self, ctx):
        """Shows your special someone that you love them - Not done"""
        logger.logDebug("yes")


def setup(bot):
    bot.add_cog(BelieverManager(bot))
