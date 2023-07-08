import enum
import os
import random
from typing import Union
import discord
from discord.ext.commands import Context
import database
from Util import logger


# ------------ COMMAND CHECKS ------------ #

async def isOwner(interaction: discord.Interaction) -> bool:
    if not interaction.user.id == 179655253392621569:
        await interaction.response.send_message("Only the owner of the bot can execute this command!", ephemeral=True)
        return False
    return True


async def isBeliever(interaction: discord.Interaction) -> bool:
    believer = database.getBeliever(interaction.user.id, interaction.guild.id)
    if believer:
        return True
    await interaction.response.send_message("You are not a believer!", ephemeral=True)
    return False


async def isPriest(interaction: discord.Interaction) -> bool:
    believer = database.getBeliever(interaction.user.id, interaction.guild.id)
    if believer:
        god = database.getGod(believer.God)
        if not god.Priest or god.Priest != believer.ID:
            await interaction.response.send_message("You are not the Priest!", ephemeral=True)
            return False
        else:
            return True
    await interaction.response.send_message("You are not a believer!", ephemeral=True)
    return False


async def isNotBeliever(interaction: discord.Interaction) -> bool:
    believer = database.getBeliever(interaction.user.id, interaction.guild.id)
    if believer:
        await interaction.response.send_message("You don't believe in any god!", ephemeral=True)
        return False
    return True


async def isMarried(interaction: discord.Interaction) -> bool:
    believer = database.getBeliever(interaction.user.id, interaction.guild.id)
    if believer:
        married = database.getMarriage(believer.ID)

        if married:
            return True
        else:
            await interaction.response.send_message("You are not married!", ephemeral=True)
            return False
    await interaction.response.send_message("You don't believe in any god!", ephemeral=True)
    return False


async def isNotMarried(interaction: discord.Interaction) -> bool:
    believer = database.getBeliever(interaction.user.id, interaction.guild.id)
    if believer:
        married = database.getMarriage(believer.ID)

        if married:
            await interaction.response.send_message("You are already married!", ephemeral=True)
            return False
    return True


async def hasOffer(interaction: discord.Interaction) -> bool:
    believer = database.getBeliever(interaction.user.id, interaction.guild.id)
    if believer:
        priestoffer = database.getPriestOffer(believer.God)
        if not priestoffer:
            await interaction.response.send_message("You don't have any offers!", ephemeral=True)
            return False
        if not priestoffer.UserID == str(interaction.user.id):
            await interaction.response.send_message("You don't have any offers!", ephemeral=True)
            return False
        return True
    await interaction.response.send_message("You don't believe in any god!", ephemeral=True)
    return False


# https://github.com/Rapptz/discord.py/blob/master/examples/views/confirm.py#LL21C4-L21C5
class MarriageConfirmUI(discord.ui.View):
    def __init__(self, user1: discord.Member, user2: discord.Member, accept_gif, deny_gif, bot_avatar, believer1: database.believers, believer2: database.believers, embedcolor):
        super().__init__(timeout=30)
        self.value = None
        self.user1 = user1
        self.user2 = user2
        self.accept_gif = accept_gif
        self.deny_gif = deny_gif
        self.bot_avatar = bot_avatar
        self.believer1 = believer1
        self.believer2 = believer2
        self.embedcolor = embedcolor

    async def on_timeout(self) -> None:
        self.clear_items()

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji='👍')
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user2.id:
            self.value = True
            self.clear_items()
            # await interaction.response.send_message("You accepted the request!", ephemeral=True)

            embed = discord.Embed(title="Marriage proposal accepted!",
                                  color=self.embedcolor,
                                  description="<@" + str(self.user1.id) + "> and <@" + str(self.user2.id) +
                                              "> are now married in the name of **" +
                                              database.getGod(self.believer1.God).Name + "**!")
            embed.set_author(name=self.user1.name + " proposed to marry " + self.user2.name,
                             icon_url=self.bot_avatar)
            database.newMarriage(self.believer1.ID, self.believer2.ID, self.believer1.God)
            embed.set_image(url=self.accept_gif)
            await interaction.response.edit_message(content="", embed=embed)

            button.disabled = True
            self.stop()
        else:
            await interaction.response.send_message("I don't believe that this request was for you...", ephemeral=True)

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red, emoji='👎')
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user2.id:
            self.value = False
            self.clear_items()
            # await interaction.response.send_message("You denied the request!", ephemeral=True)

            embed = discord.Embed(title="Marriage proposal denied!",
                                  color=self.embedcolor)
            embed.set_author(name=self.user1.name + " proposed to marry " + self.user2.name,
                             icon_url=self.bot_avatar)
            embed.set_image(url=self.deny_gif)
            await interaction.response.edit_message(content="", embed=embed)

            button.disabled = True
            self.stop()
        else:
            await interaction.response.send_message("I don't believe that this request was for you...", ephemeral=True)


class botutils:
    class GodTypes(enum.Enum):
        FROST = 1
        LOVE = 2
        EVIL = 3
        SEA = 4
        MOON = 5
        SUN = 6
        THUNDER = 7
        PARTY = 8
        WAR = 9
        WISDOM = 10
        NATURE = 11

        def getColor(self) -> discord.Color:
            if self.FROST:
                return discord.Color.blue()
            elif self.LOVE:
                return discord.Color.red()
            elif self.EVIL:
                return discord.Color.darker_grey()
            elif self.SEA:
                return discord.Color.dark_blue()
            elif self.MOON:
                return discord.Color.light_grey()
            elif self.SUN:
                return discord.Color.gold()
            elif self.THUNDER:
                return discord.Color.orange()
            elif self.PARTY:
                return discord.Color.magenta()
            elif self.WAR:
                return discord.Color.dark_red()
            elif self.WISDOM:
                return discord.Color.dark_purple()
            elif self.NATURE:
                return discord.Color.green()
            else:
                return discord.Color.dark_grey()

    # Function to get the currently used prefix
    @classmethod
    def getPrefix(cls, guildid: int) -> str:
        guildconfig = database.getGuild(guildid)

        if not guildconfig:
            return os.getenv("prefix")+"gods "
        else:
            return guildconfig.Prefix

    # Function used to try and get users from arguments
    @classmethod
    async def getUser(cls, bot: discord.ext.commands.Bot, guild: discord.Guild, arg: str) -> Union[discord.User, discord.Member]:
        if arg.startswith("<@") and arg.endswith(">"):
            userid = arg.replace("<@", "").replace(">", "").replace("!", "")  # fuck you nicknames
        else:
            userid = arg

        try:
            userid = int(userid)
        except Exception as e:
            logger.logDebug(f"Could not parse arg into userid - {e}")
            raise Exception("User not found!")

        user: Union[discord.User, discord.Member] = bot.get_user(userid)
        if user:
            logger.logDebug("User found! - %s" % user.name)
            return user

        if guild:
            try:
                user = guild.get_member(userid)
            except Exception as e:
                logger.logDebug("Member not found - guild get - %s" % e)
            if not user:
                try:
                    user = await guild.fetch_member(userid)
                except Exception as e:
                    logger.logDebug("Member not found - guild fetch - %s" % e)
        if user:
            logger.logDebug("User found! - %s" % user.name)
            return user

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
    def getGodString(cls, god: database.gods) -> str:
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
    def getGodMood(cls, moodValue: float) -> str:
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
    async def doNewPriestOffer(cls, bot: discord.ext.commands.Bot, god: database.gods, old_priestoffer: database.offers = None) -> None:
        believers = database.getBelieversByID(god.ID)

        if len(believers) >= 3:
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
                prefix = cls.getPrefix(guild.id)
                try:
                    await dm_channel.send(
                        "Congratulations! You've been selected as the priest for **" + god.Name + "** on "
                        "the " + guild.name + " server!\nWrite `"+prefix+"accept` to accept the "
                        "request, or `"+prefix+"deny` to decline the request, on that server!")
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
                                               god.Name + "**!\nWrite `" + prefix + "accept` to accept "
                                               "the request, or `" + prefix + "deny` to decline "
                                               "the request!")
                            break
                # Jump out of while loop
                break
        else:
            logger.logDebug("Not more than 3 believers in god, skipping new priest candidate check")

    @classmethod
    def disbandGod(cls, godid: int) -> bool:
        god = database.getGod(godid)
        if not god:
            return False

        believers = database.getBelieversByID(god.ID)

        if believers:
            for believer in believers:
                if not believer:
                    return True

                believer.delete_instance()

        god.delete_instance()

        return True
