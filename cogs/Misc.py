import random
from typing import Union

import aiohttp
import discord
from discord.ext import commands
from Util.botutils import botutils
import Util.botutils as utilchecks
import database
from discord import Embed, Color


class Misc(commands.Cog, name="Miscellaneous"):
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

    def __init__(self, bot):
        """Fun commands - Some of them are free, others cost Prayer Power."""
        self.bot = bot

    @commands.command(name="getcolor", aliases=["getColor", "getcolour", "getColour"], pass_context=True, no_pm=True)
    async def _getcolor(self, ctx: commands.Context, hexcode: str):
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
        await ctx.send(embed=em)

    @classmethod
    def getMiscEmbed(cls, believer, user: Union[discord.User, discord.Member], target, action):
        god = believer.God
        embedcolor = Color.dark_gold()
        if god.Type:
            for godtype, color in botutils.godtypes:
                if godtype == god.Type:
                    embedcolor = color

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

        embed.set_author(name=action_line, icon_url=user.avatar_url)
        return embed

    @commands.command(name="hug")
    @commands.check(utilchecks.isBeliever)
    async def _hug(self, ctx: commands.Context, arg1):
        """Hugs someone, awhh - 0.5 Prayer Power."""
        believer = database.getBeliever(ctx.author.id, ctx.guild.id)
        if believer.PrayerPower < 0.5:
            await ctx.send("Your Prayer Power is below 0.5! Try praying again, and then try hugging!")
            return

        target = await botutils.getUser(self.bot, ctx.guild, arg1)
        if target.id == ctx.author.id:
            await ctx.send("You cannot hug yourself! Sad, we know...")
            return
        if target.bot:
            await ctx.send("Even though I think the bot appreciates your hugs, I don't think it would feel it...")
            return

        await ctx.send(embed=self.getMiscEmbed(believer, ctx.author, target, "HUGS"))

        database.subtractPrayerPower(believer.ID, 0.5)

    @commands.command(name="love", aliases=["kiss"])
    @commands.check(utilchecks.isMarried)
    async def _love(self, ctx: commands.Context):
        """Shows your special someone that you love them - Free."""
        believer = database.getBeliever(ctx.author.id, ctx.guild.id)
        marriage = database.getMarriage(believer.ID)

        if not marriage:
            await ctx.send("You are not married, bozo!")
            return

        # Update LoveDate
        database.doLove(marriage.ID)

        # Send message
        if marriage.Believer1.UserID == str(ctx.author.id):
            loverid = marriage.Believer2.UserID
        else:
            loverid = marriage.Believer1.UserID

        target = await botutils.getUser(self.bot, ctx.guild, loverid)

        if not target:
            await ctx.send("Awwhh, lover not found...")
            return

        # await ctx.send("<@" + loverid + "> - " + ctx.author.name + " loves you!")
        await ctx.send(embed=self.getMiscEmbed(believer, ctx.author, target, "KISS"))


def setup(bot):
    bot.add_cog(Misc(bot))
