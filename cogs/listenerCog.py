import datetime
import discord
from discord.ext import commands
import database
from Util import logger
import os


class listenerCog(commands.Cog, name="Listener Cog"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # logger.logDebug("New reaction! Payload emoji name: " + payload.emoji.name)
        userid = payload.user_id
        channel = self.bot.get_channel(payload.channel_id)
        user = channel.guild.get_member(userid)

        # we check whether the reaction added is from the appeal channel
        appealguild = self.bot.get_guild(int(os.getenv('appealguild')))
        appealchannel = None
        for appealguildchannel in appealguild.channels:
            if appealguildchannel.name == "appeal-here":
                appealchannel = appealguildchannel
                break
        if appealchannel is None:
            await logger.log("No appealchannel found! Returning!", self.bot, "ERROR")
            return

        # If the channel is the appeal channel
        if payload.channel_id == appealchannel.id:
            await logger.log("A reaction has been added in the appeal channel! User ID: " + str(user.id), self.bot,
                             "DEBUG")
            if user.bot:
                return

            # Checking whether the user is banned
            if not database.isBanned(userid):
                await logger.log("An user who is not banned tried adding the ban appeal reaction! User ID: " +
                                 str(user.id), self.bot, "DEBUG")
                return

            # Checking whether the user already is verified
            if database.isAppealing(userid):
                await logger.log("Already appealing! User ID: " + str(user.id), self.bot, "DEBUG")
                return

            # Add the user to the db
            database.newBanAppeal(user.id)

            dm_channel = user.dm_channel
            if dm_channel is None:
                await user.create_dm()
                dm_channel = user.dm_channel

            # Send message
            try:
                await dm_channel.send(
                    "Thanks for your interest in appealing your WatchDog Ban!\n\nTo complete your ban "
                    "appeal, please write us a good reasoning on why YOU should get unbanned, "
                    "and why WE were wrong in banning you!")
            except Exception as e:
                # if we can't send the DM, the user probably has DM's off, at which point we would uhhh, yeah. back
                # to this later
                await logger.log(
                    "Couldn't send DM to user that reacted. User ID: " + str(user.id) + " - Error: " + str(e), self.bot,
                    "INFO")
                # send a headsup in the verification channel
                channel = self.bot.get_channel(int(os.getenv('verificationChannel')))
                await channel.send(
                    content=user.mention + " Sorry! It seems like your DM didn't go through, try to enable your DM's for this server!",
                    delete_after=float(30))
                return

        # If the channel is the banappeal channel
        if payload.channel_id == int(os.getenv('banappealschannel')):
            await logger.log("A reaction has been added in the moderator appeal channel! User ID: " + str(user.id), self.bot,
                             "DEBUG")
            if user.bot:
                return

            # Variables used
            guild = self.bot.get_guild(payload.guild_id)
            reactMember = guild.get_member(payload.user_id)
            message = await channel.fetch_message(payload.message_id)

            if payload.emoji.name == "✅" or payload.emoji.name == "❎":
                # Remove the reactions
                await message.remove_reaction(payload.emoji.name, reactMember)
                botMember = guild.get_member(self.bot.user.id)
                await message.remove_reaction("❎", botMember)
                await message.remove_reaction("✅", botMember)
            else:
                return

            appeal = database.getAppealFromMessage(message.id)
            if appeal is None:
                return
            appealUser = self.bot.get_user(int(appeal.UserID))
            ban = database.getBan(appealUser.id)
            if ban is None:
                await logger.log("Ban is none!", self.bot, "WARN")
                return
            reason = str(appeal.Reason)
            moderator = None
            if ban.Moderator is not None:
                moderator = self.bot.get_user(int(ban.Moderator))
            color = discord.Color.blurple()

            status = "None"

            # Approve
            if payload.emoji.name == "✅":
                # Basic approval stuff
                status = "Accepted"
                await self.unban(appealUser)
                database.updateBanAppealStatus(appealUser.id, True, user.id)
                color = discord.Color.green()

                # Send appeal accepted message
                await message.channel.send("Appeal accepted! " + appealUser.name + "#" + appealUser.discriminator
                                           + " has been unbanned!", delete_after=10)

                # Send unban notif in banlist
                if reactMember is not None:
                    await logger.logEmbed(color, "Moderator `%s` unbanned `%s` - (%s)" % (reactMember.name,
                                                                                          appealUser.name,
                                                                                          appealUser.id), self.bot)

                # Send private ban notif in private moderator ban list
                banlistchannel = self.bot.get_channel(int(os.getenv('prvbanlist')))
                banlistembed = discord.Embed(title="Account unbanned", color=discord.Color.green(),
                                             description="`%s` has been globally unbanned" % appealUser.id)
                if reactMember is not None:
                    banlistembed.add_field(name="Moderator", value="%s (`%s`)" % (reactMember.name + "#" +
                                                                                  reactMember.discriminator,
                                                                                  reactMember.id),
                                           inline=True)
                banlistembed.add_field(name="Name when unbanned", value="%s" % appealUser, inline=True)
                banlistembed.add_field(name="In server", value="%s (`%s`)" % (guild.name, guild.id),
                                       inline=True)
                banlistembed.add_field(name="In channel", value="%s (`%s`)" % (channel.name, channel.id),
                                       inline=True)
                banlistembed.set_footer(text="%s has been globally unbanned" % appealUser,
                                        icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                banlistembed.set_thumbnail(url=appealUser.avatar_url)
                await banlistchannel.send(embed=banlistembed)

                # Notify the user
                dm_channel = appealUser.dm_channel
                if dm_channel is None:
                    await appealUser.create_dm()
                    dm_channel = appealUser.dm_channel

                # Send message in DM's
                try:
                    await dm_channel.send(
                        "Thanks for your interest in appealing your WatchDog Ban!\n\nYour Ban Appeal has been accepted "
                        "by our Global Moderators, in other words, you are now unbanned! Don't go and get yourself "
                        "banned again!")
                except Exception as e:
                    # if we can't send the DM, the user probably has DM's off, at which point we would uhhh,
                    # yeah. back to this later
                    await logger.log(
                        "Couldn't send DM to banned user. User ID: " + str(appealUser.id) + " - Error: " + str(e), self.bot,
                        "INFO")

                # Kick the user from the appealguild
                try:
                    await appealguild.kick(appealUser)
                except Exception as e:
                    await logger.log("Could not kick user from the appeal guild after being accepted! - " + str(e), self.bot,
                                     "ERROR")
            # Deny
            elif payload.emoji.name == "❎":
                status = "Denied"
                database.updateBanAppealStatus(appealUser.id, False, user.id)
                color = discord.Color.red()

                await message.channel.send("Appeal denied! " + appealUser.name + "#" + appealUser.discriminator
                                           + " has NOT been unbanned!", delete_after=10)

                # Notify the user
                dm_channel = appealUser.dm_channel
                if dm_channel is None:
                    await appealUser.create_dm()
                    dm_channel = appealUser.dm_channel

                # Send message
                try:
                    await dm_channel.send(
                        "Thanks for your interest in appealing your WatchDog Ban!\n\nWe are sorry to inform you that "
                        "your Ban Appeal has been denied by our Global Moderators... If you believe that this is "
                        "unjustified, you can always try appealing again, by writing a new reason, "
                        "or you can try contacting the bot owner, HeroGamers#0001, directly!")
                except Exception as e:
                    # if we can't send the DM, the user probably has DM's off, at which point we would uhhh, yeah.
                    # back to this later
                    await logger.log(
                        "Couldn't send DM to banned user. User ID: " + str(appealUser.id) + " - Error: " + str(e), self.bot,
                        "INFO")

            # Update the embed
            embed = createEmbed(status + " by " + user.name + "#" + user.discriminator, color, reason, appealUser,
                                appeal, ban, moderator)
            await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(listenerCog(bot))
