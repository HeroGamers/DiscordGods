import os
import random
import discord
from discord.ext import tasks
from discord.ext import commands
import database
from Util import logger
from Util.botutils import botutils


class Tasks(commands.Cog, name="Tasks"):
    def __init__(self, bot):
        """The Cog running the tasks in the background, like clearing old invites, changing the presence etc."""
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
        # await logger.log("Updating presence...", self.bot, "DEBUG")
        try:
            await self.bot.change_presence(activity=discord.Game(name="with " + str(database.getBelieversGlobalCount())
                                                                      + " believers | " + os.getenv('prefix')
                                                                      + "gods howto"))
        except Exception as e:
            logger.logDebug("Error updating presence: " + str(e))
        self.firstrundone = True

    # ------------ GOD TASKS ------------ #

    @tasks.loop(hours=1.0)
    async def priestTask(self):
        await logger.log("Clearing expired Priest Offers...", self.bot, "DEBUG")
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
        global_mood_falloff = random.uniform(0.01, 3.0)
        global_power_falloff = random.uniform(0.01, 0.75)
        global_prayerpower_falloff = random.uniform(0.01, 0.75)

        await logger.log("Falloff Round - MoodFalloff: " + str(global_mood_falloff) + ", PowerFalloff: " +
                         str(global_power_falloff) + ", PrayerPowerFalloff: " + str(global_prayerpower_falloff),
                         self.bot, "INFO")

        database.doGodsFalloff(global_mood_falloff, global_power_falloff)
        database.doBelieverFalloffs(global_prayerpower_falloff)

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
