import asyncio
import datetime
import random

import discord
from discord.ext import commands
import database
from Util import logger
from Util.botutils import botutils


class BelieverManager(commands.Cog, name="Believer"):
    def __init__(self, bot):
        self.bot = bot
        self.proposal_gifs = ["https://cdn.discordapp.com/attachments/473953130371874828/700359948646744154/propose1.gif",
                              "https://cdn.discordapp.com/attachments/473953130371874828/700359962530152498/propose2.gif",
                              "https://cdn.discordapp.com/attachments/473953130371874828/700359970335490058/propose3.gif",
                              "https://cdn.discordapp.com/attachments/473953130371874828/700359981584875531/propose4.gif",
                              "https://cdn.discordapp.com/attachments/473953130371874828/700359991567319111/propose5.gif",
                              "https://cdn.discordapp.com/attachments/473953130371874828/700359997229498408/propose6.gif"]
        self.accept_gifs = ["https://cdn.discordapp.com/attachments/473953130371874828/700359862797729803/accept1.gif",
                            "https://cdn.discordapp.com/attachments/473953130371874828/700359881244541008/accept2.gif",
                            "https://cdn.discordapp.com/attachments/473953130371874828/700359885635715092/accept3.gif",
                            "https://cdn.discordapp.com/attachments/473953130371874828/700359894473375764/accept4.gif",
                            "https://cdn.discordapp.com/attachments/473953130371874828/700359900802580641/accept5.gif",
                            "https://cdn.discordapp.com/attachments/473953130371874828/700359929781026916/accept6.gif",
                            "https://cdn.discordapp.com/attachments/473953130371874828/700359916652855326/accept7.gif"]
        self.denial_gifs = ["https://cdn.discordapp.com/attachments/473953130371874828/700359922017239422/denial1.gif",
                            "https://cdn.discordapp.com/attachments/473953130371874828/700359937393426452/denial2.gif",
                            "https://cdn.discordapp.com/attachments/473953130371874828/700359942409945108/denial3.gif",
                            "https://cdn.discordapp.com/attachments/473953130371874828/700360012261752902/denial4.gif"]

    # ------------ BELIEVER INTERACTIONS WITH A RELIGION/GOD ------------ #

    @classmethod
    async def inGodCheck(cls, ctx):
        believer = database.getBeliever(ctx.author.id, ctx.guild.id)
        if not believer:
            await ctx.send("You are not believing in any God, yet! `/gods create <name>`!")
            return None
        return believer

    @commands.command(name="leave", aliases=["yeet"])
    async def _leave(self, ctx):
        """Leaves a religion"""
        user = ctx.author

        believer = await self.inGodCheck(ctx)
        if not believer:
            return

        if database.leaveGod(user.id, ctx.guild.id):
            await ctx.send("You've left your god!")

            # If there aren't any believers in the God anymore, disband it
            if not database.getBelieversByID(believer.God):
                database.disbandGod(believer.God)

            # If the user was married, divorce them
            marriage = database.getMarriage(believer.ID)
            if marriage:
                database.deleteMarriage(marriage.ID)
        else:
            await ctx.send("Something went wrong...")

    @commands.command(name="join", aliases=["enter"])
    async def _join(self, ctx, arg1):
        """Joins a religion"""
        if database.getBeliever(ctx.author.id, ctx.guild.id):
            await ctx.send("You are already in a God, please leave it to join a new one using `/gods leave`!")
            return

        god = database.getGodName(arg1, ctx.guild.id)
        if not god:
            await ctx.send("There is no God by that name... yet! `/gods create <name>`")
            return

        if god.InviteOnly:
            invite = database.getInvite(ctx.author.id, god.ID)
            if not invite:
                await ctx.send("That God is invite-only, and you don't have an invite...\n"
                               "Try contacting the Preist of the God for an invite!")
                return
            database.deleteInvite(invite.ID)

        database.newBeliever(ctx.author.id, god.ID)
        await ctx.send("You've now become a believer in the name of " + god.Name + "!")

    @commands.command(name="no", aliases=["deny", "decline", "reject"])
    async def _no(self, ctx):
        """Reject a proposal from your God"""
        believer = await self.inGodCheck(ctx)
        if not believer:
            return

        priestoffer = database.getPriestOffer(believer.UserID, ctx.guild.id)

        if not priestoffer:
            await ctx.send("You have no new offer from your God!")
            return

        database.deletePriestOffer(priestoffer.ID)
        await ctx.send("You have rejected " + believer.God.Name + "'s request!")

    @commands.command(name="yes", aliases=["accept"])
    async def _yes(self, ctx):
        """Accept a proposal from your God"""
        believer = await self.inGodCheck(ctx)
        if not believer:
            return

        priestoffer = database.getPriestOffer(believer.UserID, ctx.guild.id)

        if not priestoffer:
            await ctx.send("You have no new offer from your God!")
            return

        database.setPriest(believer.God.ID, believer.ID)
        database.deletePriestOffer(priestoffer.ID)
        await ctx.send("You have accepted " + believer.God.Name + "'s request!\n" + ctx.author.name + " is now the "
                       "Priest of " + believer.God.Name + "!")

    @commands.command(name="pray", aliases=["p"])
    async def _pray(self, ctx):
        """Pray to your God"""
        believer = await self.inGodCheck(ctx)
        if not believer:
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
            await ctx.send("You cannot pray to your " + botutils.getGodString(believer.God) + " yet! Time remaining: "
                           + str(round(timeTillPray, 1)) + " minutes.")

    # ------------ BELIEVER RELATIONSHIPS ------------ #

    @commands.command(name="marry", aliases=["propose"])
    async def _marry(self, ctx, arg1):
        """Marry that special someone"""
        guildid = ctx.guild.id
        user1 = ctx.author
        user2 = await botutils.getUser(self.bot, ctx.guild, arg1)

        believer1 = database.getBeliever(user1.id, guildid)
        believer2 = database.getBeliever(user2.id, guildid)

        if not believer1:
            await ctx.send("You are not believing in any religion!")
        elif database.getMarriage(believer1.ID):
            await ctx.send("You are already married?! What are you trying to do?! - "
                           "Maybe you should look at getting a divorce... `/g divorce`")
        elif not believer2:
            await ctx.send("Your special someone is not believing in any religion!")
        elif database.getMarriage(believer2.ID):
            await ctx.send("Aww... Your special someone is already married...")
        elif believer1.God != believer2.God:
            await ctx.send("You are not believing in the same God as your special someone!")
        else:
            god = believer1.God
            embedcolor = discord.Color.dark_gold()
            if god.Type:
                for type, color in botutils.godtypes:
                    if type == god.Type:
                        embedcolor = color

            embed = discord.Embed(title="Marriage proposal", color=embedcolor,
                                  description="<@" + str(user2.id) + "> - " + user1.name + " wishes to marry you! "
                                              "Do you accept their proposal, to have and to hold each other, from this "
                                              "day forward, for better, for worse, for richer, for poorer, in sickness "
                                              "and in health, until death do you apart?")
            embed.set_image(url=random.choice(self.proposal_gifs))
            embed.set_author(name=user1.name + " wishes to marry " + user2.name, icon_url=self.bot.user.avatar_url)
            message = await ctx.send("<@" + str(user2.id) + ">", embed=embed)
            await message.add_reaction('👍')
            await message.add_reaction('👎')

            def check_for_react(reaction, user):
                return user == user2 and reaction.message.id == message.id and (str(reaction.emoji) == '👍' or str(reaction.emoji) == '👎')

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_for_react)
            except asyncio.TimeoutError:
                await ctx.send("Awh, too slow!")
            else:
                accepted = str(reaction.emoji) == '👍'

                accepted_desc = str("<@" + str(user1.id) + "> and <@" + str(user2.id) + "> are now married in the name "
                                    "of **" + database.getGod(believer1.God).Name + "**!")
                state_text = "accepted" if accepted else "denied"
                embed = discord.Embed(title="Marriage proposal " + state_text + "!",
                                      color=embedcolor, description=accepted_desc if accepted else None)
                embed.set_author(name=user1.name + " proposed to marry " + user2.name, icon_url=self.bot.user.avatar_url)

                if accepted:
                    database.newMarriage(believer1.ID, believer2.ID, believer1.God)
                    embed.set_image(url=random.choice(self.accept_gifs))
                else:
                    embed.set_image(url=random.choice(self.denial_gifs))

                await message.edit(content="", embed=embed)

    @commands.command(name="divorce", aliases=["leave_with_the_kids"])
    async def _divorce(self, ctx):
        """Leave your special someone and take the kids with you"""
        believer = database.getBeliever(ctx.author.id, ctx.guild.id)
        marriage = database.getMarriage(believer.ID)

        if not marriage:
            await ctx.send("You are not married, bozo!")
            return

        # Get partner
        if marriage.Believer1.UserID == str(ctx.author.id):
            loverid = marriage.Believer2.UserID
        else:
            loverid = marriage.Believer1.UserID

        database.deleteMarriage(marriage.ID)

        lover = await botutils.getUser(self.bot, ctx.guild, loverid)
        if not lover:
            await ctx.send("Your lover could not be found!\n*But don't worry, we got ya' divorced anyway!*")
        else:
            await ctx.send(ctx.author.name + " just divorced " + lover.name + "!")

    @commands.command(name="love", aliases=["kiss"])
    async def _love(self, ctx):
        """Shows your special someone that you love them"""
        believer = database.getBeliever(ctx.author.id, ctx.guild.id)
        marriage = database.getMarriage(believer.ID)

        if not marriage:
            await ctx.send("You are not married, bozo!")
            return

        # Update LoveDate
        database.doLove(marriage.ID)

        # Send message
        if marriage.Believer1.UserID == str(ctx.author.id):
            loverid = marriage.Believer2.UserID
        else:
            loverid = marriage.Believer1.UserID
        await ctx.send("<@" + loverid + "> - " + ctx.author.name + " loves you!")


def setup(bot):
    bot.add_cog(BelieverManager(bot))
