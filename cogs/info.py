import discord
from discord import Embed
from discord.ext import commands
from Util import logger
import os


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="code", aliases=["source", "sourcecode"])
    async def _code(self, ctx):
        """View and/or help with the source code of Gods"""
        await ctx.send("The source code for Gods can be found here: https://github.com/Fido2603/DiscordGods")

    @commands.command(name="support")
    async def _support(self, ctx):
        """Get help and support regarding the bot"""
        await ctx.send("The server where the Gods roam, Treeland: https://discord.gg/PvFPEfd")

    @commands.command(name="invite")
    async def _invite(self, ctx):
        """How to invite the bot"""
        await ctx.send(
            "Invite me to your server with this link: "
            "<https://discordapp.com/oauth2/authorize?scope=bot&client_id=699403302198313011>")

    @commands.command(name="botinfo", aliases=["bot"])
    async def _botinfo(self, ctx):
        """Retrives information about the bot"""
        embed = discord.Embed(title="Bot Information", color=discord.Color.green(),
                              description="")
        embed.add_field(name="Creation Date",
                        value="%s" % discord.utils.snowflake_time(ctx.bot.user.id).strftime(
                            "%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Guilds", value="%s" % len(self.bot.guilds), inline=True)
        embed.set_footer(text="%s" % ctx.author.name,
                         icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
