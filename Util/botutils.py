import random

import discord

import database
from Util import logger


# ------------ COMMAND CHECKS ------------ #

def isBeliever(ctx):
    believer = database.getBeliever(ctx.author.id, ctx.guild.id)
    if believer:
        return True
    return False


def isPriest(ctx):
    believer = database.getBeliever(ctx.author.id, ctx.guild.id)
    if believer:
        god = database.getGod(believer.God)
        if not god.Priest or god.Priest != believer.ID:
            return False
        else:
            return True
    return False


def isNotBeliever(ctx):
    believer = database.getBeliever(ctx.author.id, ctx.guild.id)
    if believer:
        return False
    return True


def isMarried(ctx):
    believer = database.getBeliever(ctx.author.id, ctx.guild.id)
    if believer:
        married = database.getMarriage(believer.ID)

        if married:
            return True
    return False


def isNotMarried(ctx):
    believer = database.getBeliever(ctx.author.id, ctx.guild.id)
    if believer:
        married = database.getMarriage(believer.ID)

        if married:
            return False
    return True


def hasOffer(ctx):
    believer = database.getBeliever(ctx.author.id, ctx.guild.id)
    if believer:
        priestoffer = database.getPriestOffer(believer.God)
        if not priestoffer:
            return False
        if not priestoffer.UserID == str(ctx.author.id):
            return False
        return True
    return False


class botutils():
    godtypes = [("FROST", discord.Color.blue()),
                ("LOVE", discord.Color.red()),
                ("EVIL", discord.Color.darker_grey()),
                ("SEA", discord.Color.dark_blue()),
                ("MOON", discord.Color.light_grey()),
                ("SUN", discord.Color.gold()),
                ("THUNDER", discord.Color.orange()),
                ("PARTY", discord.Color.magenta()),
                ("WAR", discord.Color.dark_red()),
                ("WISDOM", discord.Color.dark_purple()),
                ("NATURE", discord.Color.green())]

    # Function used to try and get users from arguments
    @classmethod
    async def getUser(cls, bot, guild, arg):
        if arg.startswith("<@") and arg.endswith(">"):
            userid = arg.replace("<@", "").replace(">", "").replace("!", "")  # fuck you nicknames
        else:
            userid = arg

        user = None
        try:
            user = await bot.fetch_user(userid)
        except Exception as e:
            logger.logDebug("User not found! ID method - %s" % e)
            try:
                user = discord.utils.get(guild.members, name=arg)
            except Exception as e:
                logger.logDebug("User not found! Name method - %s" % e)
        if user is not None:
            logger.logDebug("User found! - %s" % user.name)
            return user
        else:
            raise Exception("User not found!")

    # Get a God's "title"/suffix depending on Gender
    @classmethod
    def getGodString(cls, god):
        god_title = "God"

        if god.Gender:
            neutral_genders = ["Non-binary", "Nb", "Neutral", "Nonbinary", "Sexless", "None"]

            if god.Gender.upper() == "Female".upper():
                god_title = "Goddess"
            elif god.Gender.upper() in (gender.upper() for gender in neutral_genders):
                god_title = "Diety"
            elif god.Gender.upper() == "Boeing AH-64 Apache".upper():
                god_title = "Attack Helicopter"

        return god_title

    # Get a God's mood
    @classmethod
    def getGodMood(cls, moodValue):
        if moodValue < -100:
            mood = "Confused"
        elif moodValue < -70:
            mood = "Angry"
        elif moodValue < -20:
            mood = "Displeased"
        elif moodValue < 20:
            mood = "Neutral"
        elif moodValue < 70:
            mood = "Pleased"
        elif moodValue <= 100:
            mood = "Exalted"
        else:
            mood = "Confused"

        return mood

    # Function to add a new priest offer to the db, and message the user about their new offer
    @classmethod
    async def doNewPriestOffer(cls, bot, god, old_priestoffer=None):
        believers = database.getBelieversByID(god.ID)

        if len(believers) >= 2:
            logger.logDebug("More than 3 believers in god, choosing new priest candidate!")
            iterations = 0
            while True:
                if iterations > 3:
                    logger.logDebug("Did over 3 iterations trying to find priest offer... Breaking")
                    break

                iterations += 1
                believer = random.choice(believers)

                if old_priestoffer is not None:
                    if believer.UserID == old_priestoffer.UserID:
                        continue

                user = await botutils.getUser(bot, bot.get_guild(believer.God.Guild), believer.UserID)

                # Update the Database with the new priest offer
                database.newPriestOffer(god.ID, user.id)

                # Get DM channel
                dm_channel = user.dm_channel
                if dm_channel is None:
                    await user.create_dm()
                    dm_channel = user.dm_channel

                # Send the message to the user about being selected as new Priest
                guild = bot.get_guild(int(god.Guild))
                try:
                    await dm_channel.send(
                        "Congratulations! You've been selected as the priest for **" + god.Name + "** on "
                        "the " + guild.name + " server!\nWrite `/gods accept` to accept the request, or "
                        "`/gods deny` to decline the request, on that server!")
                except Exception as e:
                    # if we can't send the DM, the user probably has DM's off, at which point we would uhhh, yes
                    await logger.log(
                        "Couldn't send DM to user about being selected as a priest. User ID: " + str(
                            user.id) + " - Error: "
                        + str(e), bot, "INFO")

                    # send a message to the user in a channel where the user can read, and the bot can send
                    member = guild.get_member(user.id)
                    bot_member = guild.get_member(bot.user.id)
                    for channel in guild.channels:
                        if isinstance(channel, discord.CategoryChannel) or isinstance(channel,
                                                                                      discord.VoiceChannel):
                            continue
                        user_permissions = channel.permissions_for(member)
                        bot_permissions = channel.permissions_for(bot_member)
                        if user_permissions.send_messages & bot_permissions.send_messages:
                            await channel.send("<@" + str(user.id) + "> has been selected as the priest for **" +
                                               god.Name + "**!\nWrite `/gods accept` to accept the "
                                               "request, or `/gods deny` to decline the request!")
                            break
                # Jump out of while loop
                break
        else:
            logger.logDebug("Not more than 3 believers in god, skipping new priest candidate check")
