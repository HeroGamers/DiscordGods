import discord
from Util import logger


class botutils():
    godtypes = [("FROST", discord.Color.blue()),
                ("LOVE", discord.Color.red()),
                ("EVIL", discord.Color.darker_grey()),
                ("SEA", discord.Color.dark_blue()),
                ("MOON", discord.Color.light_grey()),
                ("SUN", discord.Color.dark_orange()),
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
            neutral_genders = ["Non-binary", "Nb", "Neutral", "Nonbinary", "Sexless"]

            if god.Gender == "Female":
                god_title = "Goddess"
            elif god.Gender.upper() in (gender.upper() for gender in neutral_genders):
                god_title = "Diety"
            elif god.Gender.upper() == "Boeing AH-64 Apache".upper():
                god_title = "Attack Helicopter"

        return god_title
