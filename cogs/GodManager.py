import random
from discord.ext import commands
import database
from Util import logger
from Util.botutils import botutils
from Util import botutils as utilchecks


class GodManager(commands.Cog, name="Religion Management"):
    def __init__(self, bot):
        self.bot = bot

    # ------------ GOD MANAGEMENT ------------ #

    @commands.command(name="create", aliases=["newgod"])
    @commands.check(utilchecks.isNotBeliever)
    async def _create(self, ctx, *args):
        """Creates a new God"""
        user = ctx.author

        if database.getBeliever(user.id, ctx.guild.id):
            await ctx.send("You are already in a God, please leave it to create a new one using `/gods leave`!")
            return

        if len(args) < 1:
            await ctx.send("Please give your God a name!")
            return

        if database.getGodName(args[0], ctx.guild.id):
            await ctx.send("A God with that name already exists!")
            return

        if len(args[0]) > 16:
            await ctx.send("Please choose a name that's not longer than 16 characters!")
            return

        if len(args) > 1:
            if len(args[1]) > 19:
                await ctx.send("Please choose a gender that's not longer than 19 characters!")
                return

            god = database.newGod(ctx.guild.id, args[0], random.choice(botutils.godtypes)[0], args[1])
        else:
            god = database.newGod(ctx.guild.id, args[0], random.choice(botutils.godtypes)[0])
        if god.ID:
            await ctx.send("God created!")
            believer = database.newBeliever(user.id, god)
            if believer.ID:
                logger.logDebug("Believer created!")
        else:
            await ctx.send("Boohoo, God creation failed...")

    @commands.command(name="access", aliases=["lock", "open"])
    @commands.check(utilchecks.isPriest)
    async def _access(self, ctx):
        """Set your religion as open or invite only - Priest only"""
        god = database.getBeliever(ctx.author.id, ctx.guild.id).God

        if god:
            if database.toggleAccess(god.ID):
                await ctx.send("God is now Invite Only!")
            else:
                await ctx.send("God is now Open!")

    @commands.command(name="ally", aliases=["friend"])
    @commands.check(utilchecks.isPriest)
    async def _ally(self, ctx):
        """Toggles alliance with another religion - Not done"""
        logger.logDebug("yes")

    @commands.command(name="war", aliases=["enemy"])
    @commands.check(utilchecks.isPriest)
    async def _war(self, ctx):
        """Toggles war with another religion - Not done"""
        logger.logDebug("yes")

    @commands.command(name="description", aliases=["desc"])
    @commands.check(utilchecks.isPriest)
    async def _description(self, ctx, *args):
        """Sets a description for your religion"""
        god = database.getBeliever(ctx.author.id, ctx.guild.id).God

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
    @commands.check(utilchecks.isPriest)
    async def _invite(self, ctx, arg1):
        """Invite someone to your religion"""
        god = database.getBeliever(ctx.author.id, ctx.guild.id).God
        if god:
            user = await botutils.getUser(self.bot, ctx.guild, arg1)

            if not user:
                await ctx.send("User not found!")
                return

            if user.bot:
                await ctx.send("Sorry, but I don't think the bot is going to respond to your invitation...")
                return

            if not ctx.guild.get_member(user.id):
                await ctx.send("The user is not in this server!")
                return

            believer = database.getBeliever(user.id, ctx.guild.id)
            if believer:
                if believer.God.ID == god.ID:
                    await ctx.send(user.name + " is already in your religion!")
                    return

            invite = database.getInvite(user.id, god.ID)
            if invite:
                await ctx.send("You already have an active invite for this user to join your God! Tell them to join!")
                return

            if database.newInvite(god.ID, user.id):
                await ctx.send("An invite to your religion has been sent to the user!\n"
                               "*Invites will become invalid 24 hours after being issued.*")
            else:
                await ctx.send("Creating the invite failed!")

    @commands.command(name="settype", aliases=["typeset", "type"])
    @commands.check(utilchecks.isPriest)
    async def _settype(self, ctx, arg1):
        """Set the type of your God to something else!"""
        god = database.getBeliever(ctx.author.id, ctx.guild.id).God
        if god:
            godTypes = []
            for godTypeSet in botutils.godtypes:
                godTypes.append(godTypeSet[0])

            if arg1.upper() in godTypes:
                database.setType(god.ID, arg1.upper())
                await ctx.send("Set your God's type successfully!")
            else:
                types_string = ""
                i = 1
                for type in godTypes:
                    if i == 1:
                        types_string = type
                    else:
                        types_string = types_string + ", " + type
                    i += 1
                await ctx.send("Please choose between these types: `" + types_string + "`!")

    @commands.command(name="setgender", aliases=["genderset", "gender"])
    @commands.check(utilchecks.isPriest)
    async def _setgender(self, ctx, arg1):
        """Set the gender of your God to something else!"""
        god = database.getBeliever(ctx.author.id, ctx.guild.id).God
        if god:
            if len(arg1) > 19:
                await ctx.send("Please choose a gender that's not longer than 19 characters!")
                return

            database.setGender(god.ID, arg1)
            await ctx.send("Gender successfully set to: " + arg1 + "!")


def setup(bot):
    bot.add_cog(GodManager(bot))
