from discord.ext import commands
import database
from Util.botutils import botutils


class AdminManager(commands.Cog, name="Administrator Management"):
    def __init__(self, bot):
        """For Server Administrators to manage the Gods and how DiscordGods work on the server."""
        self.bot = bot

    # ------------ SERVER MANAGEMENT ------------ #

    @commands.command(name="setprefix", aliases=["prefix"])
    @commands.has_permissions(administrator=True)
    async def _setprefix(self, ctx, arg1):
        """Sets a custom prefix for the bot on the server."""
        if len(arg1) > 6:
            await ctx.send("Keep the prefix under 6 chars, please.")
            return

        guildconfig = database.getGuild(ctx.guild.id)

        if not guildconfig:
            guildconfig = database.newGuild(ctx.guild.id)

        database.setPrefix(guildconfig.ID, arg1)
        await ctx.send("Prefix set successfully!")

    # ------------ GOD MANAGEMENT ------------ #

    @commands.command(name="forcedescription", aliases=["forcedesc", "admindesc"])
    @commands.has_permissions(administrator=True)
    async def _forcedescription(self, ctx, *args):
        """Forces a description for a religion."""
        if len(args) < 2:
            await ctx.send("Include both a name and a description!")
            return

        god = database.getGodName(args[0], ctx.guild.id)

        if god:
            desc = ""
            i = 1
            for arg in args:
                if i > 1:
                    desc = desc + " " + arg
                i += 1
            desc.strip()

            if len(desc) > 100:
                await ctx.send("Keep the description under 100 chars, please.")
                return

            database.setDesc(god.ID, desc)
            await ctx.send("Description set successfully!")
        else:
            await ctx.send("No God found by that name!")

    @commands.command(name="forcesettype", aliases=["forcetypeset", "forcetype"])
    @commands.has_permissions(administrator=True)
    async def _forcesettype(self, ctx, *args):
        """Set the type of a God to something else."""
        if len(args) < 2:
            await ctx.send("Include both a name and a type!")
            return

        god = database.getGodName(args[0], ctx.guild.id)
        if god:
            godtypes = []
            for godTypeSet in botutils.godtypes:
                godtypes.append(godTypeSet[0])

            if args[1].upper() in godtypes:
                database.setType(god.ID, args[1].upper())
                await ctx.send("Set your God's type successfully!")
            else:
                types_string = ""
                i = 1
                for godtype in godtypes:
                    if i == 1:
                        types_string = godtype
                    else:
                        types_string = types_string + ", " + godtype
                    i += 1
                await ctx.send("Please choose between these types: `" + types_string + "`!")

    @commands.command(name="forcesetgender", aliases=["forcegenderset", "forcegender"])
    @commands.has_permissions(administrator=True)
    async def _forcesetgender(self, ctx, *args):
        """Set the gender of a God to something else."""
        if len(args) < 2:
            await ctx.send("Include both a name and a gender!")
            return

        god = database.getGodName(args[0], ctx.guild.id)
        if god:
            if len(args[1]) > 19:
                await ctx.send("Please choose a gender that's not longer than 19 characters!")
                return

            database.setGender(god.ID, args[1])
            await ctx.send("Gender successfully set to: " + args[1] + "!")

    @commands.command(name="forcesetpriest", aliases=["forcepriest", "adminpriest"])
    @commands.has_permissions(administrator=True)
    async def _forcesetpriest(self, ctx, *args):
        """Set the priest of a God."""
        if len(args) < 2:
            await ctx.send("Include both a name and a user.")
            return

        god = database.getGodName(args[0], ctx.guild.id)
        if god:
            user = await botutils.getUser(self.bot, ctx.guild, args[1])
            if not user:
                await ctx.send("Could not fetch user!")
                return

            if not ctx.guild.get_member(user.id):
                await ctx.send("User is not in this server!")

            believer = database.getBeliever(user.id, ctx.guild.id)

            if believer:
                if believer.God.ID != god.ID:
                    database.setGod(believer.ID, god.ID)
            else:
                believer = database.newBeliever(user.id, god.ID)

            database.setPriest(god.ID, believer.ID)

            await ctx.send("Priest successfully set!")

    @commands.command(name="forcedeletegod", aliases=["deletegod", "removegod", "forcedisbandgod"])
    @commands.has_permissions(administrator=True)
    async def _forcedeletegod(self, ctx, arg1):
        """Removes a religion from the server."""
        god = database.getGodName(arg1, ctx.guild.id)
        if god:
            if botutils.disbandGod(god.ID):
                await ctx.send("God disbanded successfully!")
            else:
                await ctx.send("An error occurred doing that!")
        else:
            await ctx.send("A god with that name doesn't exist!")

    @commands.command(name="forcerename", aliases=["frn"]) #My attempt to make a possibility to change god's name (mrSheploo)
    @commands.has_permissions(administrator=True)
    async def _rename(self, ctx, arg1):
        """Rename existing God."""
        god = database.getGodName(arg1, ctx.guild.id)
        
        database.rename(god.ID, arg1)
        await. ctx.send("God's name successfully changed to: " + arg1 + "!")



def setup(bot):
    bot.add_cog(AdminManager(bot))
