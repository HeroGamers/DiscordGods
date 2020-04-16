import json
import os
import requests
from discord.ext import commands, tasks
import dbl
from Util import logger


class BotLists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.topgg_token = os.getenv('top.gg_token')  # https://top.gg/
        self.dbotsgg_token = os.getenv('discord.bots.gg_token')  # https://discord.bots.gg/
        self.discordbotlistcom_token = os.getenv('discordbotlist.com_token')  # https://discordbotlist.com/
        self.botsondiscordxyz_token = os.getenv('bots.ondiscord.xyz_token')  # https://bots.ondiscord.xyz/

        self.topgg = dbl.DBLClient(self.bot, self.topgg_token)  # top.gg

        self.update_stats.start()

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update the server count across multiple bot lists."""
        guilds = len(self.bot.guilds)
        users = len(set(self.bot.get_all_members()))
        id = str(self.bot.user.id)
        logger.logDebug("Attempting to post server counts...", "INFO")

        # top.gg
        site = "top.gg"
        try:
            await self.topgg.post_guild_count()
            logger.logDebug('Posted server count to ' + site + ' ({})'.format(self.topgg.guild_count()), "INFO")
        except Exception as e:
            logger.logDebug('Failed to post server count to ' + site + ': {} - {}'.format(type(e).__name__, e), "INFO")

        # discord.bots.gg
        site = "discord.bots.gg"
        headers = {'Authorization': self.dbotsgg_token,
                   'Content-Type': "application/json"}
        payload = {'guildCount': guilds}
        url = "https://discord.bots.gg/api/v1/bots/" + id + "/stats"
        resp = requests.post(url=url, headers=headers, data=json.dumps(payload))
        logger.logDebug("Response from " + site + ": " + str(resp), "INFO")

        # discordbotlist.com
        site = "discordbotlist.com"
        headers = {'Authorization': "Bot " + self.discordbotlistcom_token,
                   'Content-Type': "application/json"}
        payload = {'guilds': guilds,
                   'users': users}
        url = "https://discordbotlist.com/api/bots/" + id + "/stats"
        resp = requests.post(url=url, headers=headers, data=json.dumps(payload))
        logger.logDebug("Response from " + site + ": " + str(resp), "INFO")

        # bots.ondiscord.xyz
        site = "bots.ondiscord.xyz"
        headers = {'Authorization': self.botsondiscordxyz_token,
                   'Content-Type': "application/json"}
        payload = {'guildCount': guilds}
        url = "https://discordbotlist.com/bot-api/bots/" + id + "/guilds"
        resp = requests.post(url=url, headers=headers, data=json.dumps(payload))
        logger.logDebug("Response from " + site + ": " + str(resp), "INFO")

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(BotLists(bot))
