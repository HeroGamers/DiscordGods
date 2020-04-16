import random
import discord
from discord.ext import tasks
from discord.ext import commands
import database
from Util import logger
from Util.botutils import botutils
import datetime


class Tasks(commands.Cog, name="Tasks"):
    def __init__(self, bot):
        self.bot = bot
        self.clearOldInvites.start()
        # self.priestTask.start()

    def cog_unload(self):
        self.clearOldInvites.cancel()
        self.priestTask.cancel()

    # ------------ GOD MANAGEMENT TASKS ------------ #

    @tasks.loop(hours=1.0)
    async def priestTask(self):
        await logger.log("Clearing expired Priest Offers...", self.bot, "DEBUG")
        date = datetime.datetime.today()
        priestoffers = database.clearOldPriestOffers(date)
        await logger.log("Cleared expired Priest Offers!", self.bot, "DEBUG")

        async def doNewPriestOffer(god, user):
            # Update the Database with the new priest offer
            database.newPriestOffer(priestoffer.God.ID, believer.UserID)

            # Get DM channel
            dm_channel = user.dm_channel
            if dm_channel is None:
                await user.create_dm()
                dm_channel = user.dm_channel

            # Send the message to the user about being selected as new Priest
            guild = self.bot.get_guild(god.Guild)
            try:
                await dm_channel.send("Congratulations! You've been selected as the priest for **" + god.name + "** on "
                                      "the " + guild.name + " server!\nWrite `/gods accept` to accept the request, or "
                                                            "`/gods deny` to decline the request, on that server!")
            except Exception as e:
                # if we can't send the DM, the user probably has DM's off, at which point we would uhhh, yes
                await logger.log(
                    "Couldn't send DM to user about being selected as a priest. User ID: " + str(user.id) + " - Error: " + str(e), self.bot,
                    "INFO")

                # send a message to the user in a channel where the user can read, and the bot can send
                member = guild.get_member(user.id)
                bot_member = guild.get_member(self.bot.user.id)
                for channel in guild.channels:
                        if isinstance(channel, discord.CategoryChannel) or isinstance(channel, discord.VoiceChannel):
                            continue
                        user_permissions = channel.permissions_for(member)
                        if user_permissions.read_messages:
                            bot_permissions = channel.permissions_for(bot_member)
                            if bot_permissions.send_messages:
                                await channel.send(user.name + " has been selected as the priest for **" +
                                                   god.name + "**!\nWrite `/gods accept` to accept the request, or "
                                                              "`/gods deny` to decline the request!")
                                break

        # Select a new priest for each God, if the God still qualifies
        for priestoffer in priestoffers:
            believers = database.getBelieversByID(priestoffer.God.ID)

            if len(believers) >= 3:
                logger.logDebug("More than 3 believers in god, choosing new priest candidate!")
                while True:
                    believer = random.choice(believers)
                    if believer.UserID != priestoffer.UserID:
                        user = await botutils.getUser(self.bot, self.bot.get_guild(believer.God.Guild), believer.UserID)
                        await doNewPriestOffer(believer.God, user)

            else:
                logger.logDebug("Not more than 3 believers in god, skipping new priest candidate check")

    # ------------ BELIEVER TASKS ------------ #

    @tasks.loop(hours=5.0)
    async def clearOldInvites(self):
        await logger.log("Clearing expired God Invites...", self.bot, "DEBUG")
        database.clearExpiredInvites()
        await logger.log("Cleared expired God Invites!", self.bot, "DEBUG")


def setup(bot):
    bot.add_cog(Tasks(bot))
