import os
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

        self.firstrundone = False

        self.doFalloffs.start()
        self.clearOldInvites.start()
        self.priestTask.start()
        self.doPresenceUpdate.start()

    def cog_unload(self):
        self.doFalloffs.cancel()
        self.clearOldInvites.cancel()
        self.priestTask.cancel()
        self.doPresenceUpdate.cancel()

    # ------------ PLUGIN TASKS ------------ #

    @tasks.loop(minutes=30.0)
    async def doPresenceUpdate(self):
        try:
            await self.bot.change_presence(activity=discord.Game(name="with " + str(database.getBelieversGlobalCount()) + " believers | " + os.getenv('prefix') + "gods help"))
        except Exception as e:
            logger.logDebug("Error updating presence: " + str(e))
        self.firstrundone = True

    # ------------ GOD TASKS ------------ #

    @tasks.loop(hours=1.0)
    async def priestTask(self):
        await logger.log("Clearing expired Priest Offers...", self.bot, "DEBUG")
        date = datetime.datetime.today()
        priestoffers = database.clearOldPriestOffers()
        await logger.log("Cleared expired Priest Offers!", self.bot, "DEBUG")

        # Select a new priest for each God, if the God still qualifies
        for priestoffer in priestoffers:
            await botutils.doNewPriestOffer(self.bot, priestoffer.God, priestoffer)

    @tasks.loop(hours=1.5)
    async def doFalloffs(self):
        if not self.firstrundone:
            return

        await logger.log("Running Falloff's Task...", self.bot, "DEBUG")
        globalMoodFalloff = random.uniform(0.01, 3.0)
        globalPowerFalloff = random.uniform(0.01, 0.75)
        globalPrayerPowerFalloff = random.uniform(0.01, 0.75)

        await logger.log("Falloff Round - MoodFalloff: " + str(globalMoodFalloff) + ", PowerFalloff: " +
                         str(globalPowerFalloff) + ", PrayerPowerFalloff: " + str(globalPrayerPowerFalloff),
                         self.bot, "INFO")

        database.doGodsFalloff(globalMoodFalloff, globalPowerFalloff)
        database.doBelieverFalloffs(globalPrayerPowerFalloff)

    # ------------ BELIEVER TASKS ------------ #

    @tasks.loop(hours=5.0)
    async def clearOldInvites(self):
        await logger.log("Clearing expired God Invites...", self.bot, "DEBUG")
        database.clearExpiredInvites()
        await logger.log("Cleared expired God Invites!", self.bot, "DEBUG")

    # ------------ WAIT FOR BOT READY ------------ #

    @doPresenceUpdate.before_loop
    @priestTask.before_loop
    @doFalloffs.before_loop
    @clearOldInvites.before_loop
    async def before_loops(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Tasks(bot))
