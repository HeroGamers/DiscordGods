import discord
from discord.ext import commands
from Util import logger


class essentials(commands.Cog, name="Essentials"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="loadcog", aliases=["loadextension"])
    @commands.is_owner()
    async def _loadcog(self, ctx, arg1):
        """Loads a cog"""
        bot = self.bot
        try:
            bot.load_extension(f"cogs.{arg1}")
            await ctx.send(f"Successfully loaded the {arg1} extension")
            await logger.log("Moderator `%s` loaded the extension %s" % (ctx.author.name, arg1), bot, "INFO")
        except Exception as e:
            await ctx.send(f"Failed to load the extension {arg1}")
            await logger.log(f"Failed to load the extension {arg1} - {e}", bot, "ERROR")

    @commands.command(name="listcogs", aliases=["cogs"])
    @commands.is_owner()
    async def _listcogs(self, ctx):
        """Lists all the cogs"""
        embed = discord.Embed(title="Cogs", color=discord.Color.green(),
                              description="`essentials, info, botlists, listenerCog, GodManager`")
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="unloadcog", aliases=["unloadextension"])
    @commands.is_owner()
    async def _unloadcog(self, ctx, arg1):
        """Unloads a cog"""
        bot = self.bot
        try:
            bot.unload_extension(f"cogs.{arg1}")
            await ctx.send(f"Successfully unloaded the {arg1} extension")
            await logger.log("Moderator `%s` unloaded the extension %s" % (ctx.author.name, arg1), bot, "INFO")
        except Exception as e:
            await ctx.send(f"Failed to unload the extension {arg1}")
            await logger.log(f"Failed to unload the extension {arg1} - {e}", bot, "ERROR")


def setup(bot):
    bot.add_cog(essentials(bot))
