import aiohttp
import discord
from discord.ext import commands


class Misc(commands.Cog, name="Miscellaneous"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="getcolor", aliases=["getColor", "getcolour", "getColour"], pass_context=True, no_pm=True)
    async def _getcolor(self, ctx, hexcode: str):
        """Gets information about a color from its HEX code"""
        hexcode = hexcode.strip('#')
        url = "https://api.color.pizza/v1/{}".format(hexcode)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
        hexapi = 'http://www.htmlcsscolor.com/preview/gallery/{}.png'.format(data["colors"][0]["hex"].strip('#'))
        em = discord.Embed(color=int('0x' + hexcode, 16))
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


def setup(bot):
    bot.add_cog(Misc(bot))
