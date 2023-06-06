import random
from typing import Union
import aiohttp
import discord
from discord.ext import commands
from Util.botutils import botutils
import Util.botutils as utilchecks
import database
from discord import Embed, Color, app_commands


class Misc(app_commands.Group, name="miscellaneous"):
    hug_lines = ["{user} hugs {target}! Awaaa~", "{user} hugs {target} tightly!"]
    kiss_lines = ["{user} loves {target}!", "{user} kisses {target}!", "{user} loves {target} so, so very much!"]
    hug_gifs = ["https://cdn.discordapp.com/attachments/473953130371874828/704725705098788874/hug1.gif",
                "https://cdn.discordapp.com/attachments/473953130371874828/704725689613418646/hug2.gif",
                "https://cdn.discordapp.com/attachments/473953130371874828/704725700300636351/hug3.gif",
                "https://cdn.discordapp.com/attachments/473953130371874828/704725701839945728/hug4.gif"]
    kiss_gifs = ["https://cdn.discordapp.com/attachments/473953130371874828/704727485132046537/kiss1.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727464072577104/kiss2.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727475388809266/kiss3.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727484565815417/kiss4.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727485283172383/kiss5.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727487980241026/kiss6.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727491335422042/kiss7.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727514425327646/kiss8.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727493466128524/kiss9.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727499161993236/kiss10.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727500667879564/kiss11.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727517478649906/kiss12.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727542342484098/kiss13.gif",
                 "https://cdn.discordapp.com/attachments/473953130371874828/704727515671035954/kiss14.gif"]
    yaoi_kiss_gifs = ["https://cdn.discordapp.com/attachments/473953130371874828/704727484565815417/kiss4.gif",
                      "https://cdn.discordapp.com/attachments/473953130371874828/704727493466128524/kiss9.gif",
                      "https://cdn.discordapp.com/attachments/473953130371874828/704727499161993236/kiss10.gif",
                      "https://cdn.discordapp.com/attachments/473953130371874828/704727500667879564/kiss11.gif",
                      "https://cdn.discordapp.com/attachments/473953130371874828/704727517478649906/kiss12.gif",
                      "https://cdn.discordapp.com/attachments/473953130371874828/704727542342484098/kiss13.gif",
                      "https://cdn.discordapp.com/attachments/473953130371874828/704727515671035954/kiss14.gif"]

    def __init__(self, bot: discord.ext.commands.Bot):
        """Fun commands - Some of them are free, others cost Prayer Power."""
        super().__init__()
        self.bot = bot

    # I believe this was a command that my boyfriend made (shoutout to Isla), from their old bot, and forced me
    # to add it
    @app_commands.command(name="getcolor")
    async def _getcolor(self, interaction: discord.Interaction, hexcode: str):
        """Gets information about a color from its HEX code."""
        hexcode = hexcode.strip('#')
        url = "https://api.color.pizza/v1/{}".format(hexcode)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
        hexapi = 'http://www.htmlcsscolor.com/preview/gallery/{}.png'.format(data["colors"][0]["hex"].strip('#'))
        em = Embed(color=int('0x' + hexcode, 16))
        em.set_image(url=hexapi)
        em.add_field(name='Name:', value=data["colors"][0]["name"], inline=True)
        em.add_field(name='Hex:', value=data["colors"][0]["hex"].upper(), inline=True)
        em.add_field(name='RGB:', value='R: ' + str(data["colors"][0]["rgb"]["r"]) + '; G: ' + str(
            data["colors"][0]["rgb"]["g"]) + '; B: ' + str(data["colors"][0]["rgb"]["b"]), inline=True)
        em.add_field(name='Luminance:', value=data["colors"][0]["luminance"], inline=True)
        em.add_field(name='Distance:', value=data["colors"][0]["distance"], inline=True)
        em.add_field(name='Requested Hex:', value=data["colors"][0]["requestedHex"].upper(), inline=True)
        em.set_footer(text='<== Original requested color; other color\'s values might be approximated',
                      icon_url="http://www.htmlcsscolor.com/preview/gallery/{}.png".format(data["colors"][0]["requestedHex"].strip('#')))
        await interaction.response.send_message(embed=em, ephemeral=True)

    @classmethod
    def getMiscEmbed(cls, believer, user: Union[discord.User, discord.Member], target: Union[discord.User, discord.Member], action: str):
        god = believer.God
        embedcolor = Color.dark_gold()
        if god.Type:
            for godtype in botutils.GodTypes:
                if godtype.name == god.Type:
                    embedcolor = godtype.getColor()

        # Create embed
        embed = Embed(color=embedcolor)

        # Get action line
        if "hug" in action.lower():
            action_line = random.choice(cls.hug_lines).replace("{user}", user.name).replace("{target}", target.name)
            embed.set_image(url=random.choice(cls.hug_gifs))
        elif "kiss" in action.lower():
            action_line = random.choice(cls.kiss_lines).replace("{user}", user.name).replace("{target}", target.name)
            if user.id == 199436790581559296 or target.id == 199436790581559296:
                embed.set_image(url=random.choice(cls.yaoi_kiss_gifs))
            else:
                embed.set_image(url=random.choice(cls.kiss_gifs))
        else:
            action_line = "Error!"

        embed.set_author(name=action_line, icon_url=user.avatar)
        return embed

    @app_commands.command(name="hug")
    @app_commands.check(utilchecks.isBeliever)
    async def _hug(self, interaction: discord.Interaction, user: discord.Member):
        """Hugs someone, awhh - 0.5 Prayer Power."""
        believer = database.getBeliever(interaction.user.id, interaction.guild.id)
        if believer.PrayerPower < 0.5:
            await interaction.response.send_message("Your Prayer Power is below 0.5! Try praying again, and then try hugging!", ephemeral=True)
            return

        if user.id == interaction.user.id:
            await interaction.response.send_message("You cannot hug yourself! Sad, we know...", ephemeral=True)
            return
        if user.bot:
            await interaction.response.send_message("Even though I think the bot appreciates your hugs, I don't think it would feel it...", ephemeral=True)
            return

        await interaction.response.send_message(embed=self.getMiscEmbed(believer, interaction.user, user, "HUGS"))

        database.subtractPrayerPower(believer.ID, 0.5)

    @app_commands.command(name="love")
    @app_commands.check(utilchecks.isMarried)
    async def _love(self, interaction: discord.Interaction):
        """Shows your special someone that you love them - Free."""
        believer = database.getBeliever(interaction.user.id, interaction.guild.id)
        if not believer:
            await interaction.response.send_message("You don't believe in any god.", ephemeral=True)
            return
        marriage = database.getMarriage(believer.ID)

        if not marriage:
            await interaction.response.send_message("You are not married, bozo!", ephemeral=True)
            return

        # Update LoveDate
        database.doLove(marriage.ID)

        # Send message
        if marriage.Believer1.UserID == str(interaction.user.id):
            loverid = marriage.Believer2.UserID
        else:
            loverid = marriage.Believer1.UserID

        target = await botutils.getUser(self.bot, interaction.guild, loverid)

        if not target:
            await interaction.response.send_message("Awwhh, lover not found...", ephemeral=True)
            return

        # await interaction.response.send_message("<@" + loverid + "> - " + interaction.user.name + " loves you!")
        await interaction.response.send_message(embed=self.getMiscEmbed(believer, interaction.user, target, "KISS"))
