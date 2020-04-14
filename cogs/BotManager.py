import discord
from discord.ext import commands
from Util import logger


class BotManager(commands.Cog, name="Bot Commands"):
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

    @commands.command(name="botinvite", aliases=["invitebot", "addbot"])
    async def _botinvite(self, ctx):
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
    bot.add_cog(BotManager(bot))
