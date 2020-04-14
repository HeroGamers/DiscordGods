import os, sys
from discord import Embed
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime


def setup_logger():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%H:%M:%S')
    handler = TimedRotatingFileHandler("logs/gods.log", when="midnight", interval=1, encoding="UTF-8")
    handler.suffix = "%Y%m%d"
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger("watchdog")
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    logger.setLevel(logging.DEBUG)


async def log(message, bot, level="INFO", debug=""):
    if (os.getenv('debugEnabled') == "False") and (level == "DEBUG"):
        return

    channel = bot.get_channel(int(os.getenv('botlog')))
    time = datetime.datetime.now().strftime('%H:%M:%S')

    if level == "DEBUG":
        levelemote = "🔧"
    elif level == "ERROR":
        levelemote = "❌"
    elif level == "WARNING":
        levelemote = "❗"
    elif level == "CRITICAL":
        levelemote = "🔥"
    else:
        levelemote = "🔎"

    await channel.send("`[" + time + "]` **" + levelemote + " " + level + ":** " + message)
    if debug == "":
        logDebug(message, level)
        return
    logDebug(debug, level)


def logDebug(message, level="INFO"):
    if (os.getenv('debugEnabled') == "False") and (level == "DEBUG"):
        return

    logger = logging.getLogger("watchdog")
    if level == "DEBUG":
        logger.debug(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "CRITICAL":
        logger.critical(message)
    else:
        logger.info(message)


async def logEmbed(color, description, bot, debug=""):
    channel = bot.get_channel(int(os.getenv('botlog')))
    await channel.send(embed=Embed(color=color, description=description, timestamp=datetime.datetime.now()))
    if debug == "":
        logDebug(description)
        return
    logDebug(debug)
