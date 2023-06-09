import datetime
import random
import discord
from discord import app_commands
from discord.ext import commands
import database
from Util import logger
from Util.botutils import botutils, MarriageConfirmUI
from Util import botutils as utilchecks


@app_commands.guild_only()
class BelieverManager(app_commands.Group, name="believer"):
    def __init__(self, bot: commands.Bot):
        """For all your believer needs! Join and leave religions, get married etc."""
        super().__init__()
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

    @app_commands.command(name="leave")
    @app_commands.check(utilchecks.isBeliever)
    async def _leave(self, interaction: discord.Interaction):
        """Leaves a religion."""
        user = interaction.user

        believer = database.getBeliever(interaction.user.id, interaction.guild.id)
        if not believer:
            return

        if database.leaveGod(user.id, interaction.guild.id):
            await interaction.response.send_message("You've left your god!", ephemeral=True)

            # If there aren't any believers in the God anymore, disband it
            if not database.getBelieversByID(believer.God):
                database.disbandGod(believer.God)
            elif believer.God.Priest == believer.ID:
                database.setPriest(believer.God.ID, None)

            # If the user was married, divorce them
            marriage = database.getMarriage(believer.ID)
            if marriage:
                database.deleteMarriage(marriage.ID)
        else:
            await interaction.response.send_message("Something went wrong...", ephemeral=True)

    @app_commands.command(name="join")
    @app_commands.check(utilchecks.isNotBeliever)
    async def _join(self, interaction: discord.Interaction, name: str):
        """Joins a religion."""
        believer = database.getBeliever(interaction.user.id, interaction.guild.id)
        if believer:
            if name.upper() == believer.God.Name.upper():
                await interaction.response.send_message("You are already believing in this God!", ephemeral=True)
                return
            await interaction.response.send_message("You are already in a God, please leave it to join a new one!", ephemeral=True)
            return

        god = database.getGodName(name, interaction.guild.id)
        if not god:
            await interaction.response.send_message("There is no God by that name... yet!", ephemeral=True)
            return

        if god.InviteOnly:
            invite = database.getInvite(interaction.user.id, god.ID)
            if not invite:
                await interaction.response.send_message("That God is invite-only, and you don't have an invite...\n"
                               "Try contacting the Priest of the God for an invite!", ephemeral=True)
                return
            database.deleteInvite(invite.ID)

        database.newBeliever(interaction.user.id, god.ID)
        await interaction.response.send_message("You've now become a believer in the name of " + god.Name + "!", ephemeral=True)

        priestoffer = database.getPriestOffer(god.ID)

        print(priestoffer)

        if not god.Priest and not database.getPriestOffer(god.ID):
            await botutils.doNewPriestOffer(self.bot, god)
            logger.logDebug("Sent a new priest offer, God reached 3 believers!")
        else:
            logger.logDebug("God already had a preist or a priest offer")

    @app_commands.command(name="deny")
    @app_commands.check(utilchecks.hasOffer)
    async def _no(self, interaction: discord.Interaction):
        """Reject a proposal from your God."""
        believer = database.getBeliever(interaction.user.id, interaction.guild.id)
        priestoffer = database.getPriestOffer(believer.God.ID)

        database.deletePriestOffer(priestoffer.ID)
        await interaction.response.send_message("You have rejected " + believer.God.Name + "'s request!", ephemeral=True)
        await botutils.doNewPriestOffer(self.bot, priestoffer.God, priestoffer)

    @app_commands.command(name="accept")
    @app_commands.check(utilchecks.hasOffer)
    async def _yes(self, interaction: discord.Interaction):
        """Accept a proposal from your God."""
        believer = database.getBeliever(interaction.user.id, interaction.guild.id)
        if not believer:
            await interaction.response.send_message("You don't believe in any god", ephemeral=True)
            return
        priestoffer = database.getPriestOffer(believer.God.ID)
        if not priestoffer:
            await interaction.response.send_message("You don't have any offers", ephemeral=True)
            return

        database.setPriest(believer.God.ID, believer.ID)
        database.deletePriestOffer(priestoffer.ID)
        await interaction.response.send_message("You have accepted " + believer.God.Name + "'s request!\n" + interaction.user.name + " is now the "
                       "Priest of " + believer.God.Name + "!")

    @app_commands.command(name="pray")
    @app_commands.check(utilchecks.isBeliever)
    async def _pray(self, interaction: discord.Interaction, show: bool = True):
        """Pray to your God."""
        believer = database.getBeliever(interaction.user.id, interaction.guild.id)
        if not believer:
            await interaction.response.send_message(
                "You don't believe in any god!", ephemeral=True)
            return

        date = datetime.datetime.now()
        timediff = date - believer.PrayDate
        minutes = timediff.total_seconds()/60

        if minutes >= 30:
            database.pray(believer)
            believer = database.getBelieverByID(believer.ID)

            await interaction.response.send_message(f"You prayed to {believer.God.name if believer.God else ('your ' + botutils.getGodString(believer.God))}! Your prayer power is now **{round(believer.PrayerPower, 2)}**!", ephemeral=show)
        else:
            time_till_pray = 30-minutes
            await interaction.response.send_message("You cannot pray to your " + botutils.getGodString(believer.God) + " yet! Time remaining: "
                           + str(round(time_till_pray, 1)) + " minutes.", ephemeral=True)

    # ------------ BELIEVER RELATIONSHIPS ------------ #

    @app_commands.command(name="marry")
    @app_commands.check(utilchecks.isBeliever)
    @app_commands.check(utilchecks.isNotMarried)
    async def _marry(self, interaction: discord.Interaction, special_someone: discord.Member):
        """Marry that special someone."""
        guildid = interaction.guild.id
        user1 = interaction.user
        user2 = special_someone

        believer1 = database.getBeliever(user1.id, guildid)
        believer2 = database.getBeliever(user2.id, guildid)

        if not believer1:
            await interaction.response.send_message("You are not believing in any religion!", ephemeral=True)
        elif database.getMarriage(believer1.ID):
            await interaction.response.send_message("You are already married?! What are you trying to do?! - "
                           "Maybe you should look at getting a divorce...", ephemeral=True)
        elif not believer2:
            await interaction.response.send_message("Your special someone is not believing in any religion!", ephemeral=True)
        elif database.getMarriage(believer2.ID):
            await interaction.response.send_message("Aww... Your special someone is already married...", ephemeral=True)
        elif believer1.God != believer2.God:
            await interaction.response.send_message("You are not believing in the same God as your special someone!", ephemeral=True)
        elif believer1 == believer2:
            await interaction.response.send_message("You can't marry yourself, bozo!", ephemeral=True)
        else:
            god = believer1.God
            embedcolor = discord.Color.dark_gold()
            if god.Type:
                for godtype in botutils.GodTypes:
                    if godtype.name == god.Type:
                        embedcolor = godtype.getColor()

            embed = discord.Embed(title="Marriage proposal", color=embedcolor,
                                  description="<@" + str(user2.id) + "> - " + user1.name + " wishes to marry you! "
                                              "Do you accept their proposal, to have and to hold each other, from this "
                                              "day forward, for better, for worse, for richer, for poorer, in sickness "
                                              "and in health, until death do you apart?")
            embed.set_image(url=random.choice(self.proposal_gifs))
            embed.set_author(name=user1.name + " wishes to marry " + user2.name, icon_url=self.bot.user.avatar)

            marriage_view = MarriageConfirmUI(user1, user2, random.choice(self.accept_gifs), random.choice(self.denial_gifs),
                                              self.bot.user.avatar, believer1, believer2, embedcolor)
            await interaction.response.send_message("<@" + str(user2.id) + ">", embed=embed, view=marriage_view)

            # logger.logDebug("Waiting for marriage request")
            # if await marriage_view.wait():
            #     logger.logDebug("timeout 1")
            #     await interaction.response.edit_message(content="Awh, too slow!", embed=None)
            #     return
            #
            # if marriage_view.value is None:
            #     logger.logDebug("timeout 2")
            #     await interaction.response.edit_message(content="Awh, too slow!", embed=None)
            #     return
            # elif marriage_view.value:
            #     logger.logDebug("accepted")
            #     embed = discord.Embed(title="Marriage proposal accepted!",
            #                           color=embedcolor,
            #                           description="<@" + str(user1.id) + "> and <@" + str(user2.id) +
            #                                       "> are now married in the name of **" +
            #                                       database.getGod(believer1.God).Name + "**!")
            #     embed.set_author(name=user1.name + " proposed to marry " + user2.name,
            #                      icon_url=self.bot.user.avatar)
            #     database.newMarriage(believer1.ID, believer2.ID, believer1.God)
            #     embed.set_image(url=random.choice(self.accept_gifs))
            # else:
            #     logger.logDebug("denied")
            #     embed = discord.Embed(title="Marriage proposal denied!",
            #                           color=embedcolor)
            #     embed.set_author(name=user1.name + " proposed to marry " + user2.name,
            #                      icon_url=self.bot.user.avatar)
            #     embed.set_image(url=random.choice(self.denial_gifs))
            # logger.logDebug("sending")
            # await interaction.response.edit_message(content="", embed=embed)

    @app_commands.command(name="divorce")
    @app_commands.check(utilchecks.isMarried)
    async def _divorce(self, interaction: discord.Interaction):
        """Leave your special someone and take the kids with you."""
        believer = database.getBeliever(interaction.user.id, interaction.guild.id)
        marriage = database.getMarriage(believer.ID)

        if not marriage:
            await interaction.response.send_message("You are not married, bozo!", ephemeral=True)
            return

        # Get partner
        if marriage.Believer1.UserID == str(interaction.user.id):
            loverid = marriage.Believer2.UserID
        else:
            loverid = marriage.Believer1.UserID

        database.deleteMarriage(marriage.ID)

        lover = await botutils.getUser(self.bot, interaction.guild, loverid)
        if not lover:
            await interaction.response.send_message("Your lover could not be found!\n*But don't worry, we got ya' divorced anyway!*", ephemeral=True)
        else:
            await interaction.response.send_message(interaction.user.name + " just divorced " + lover.name + "!")
