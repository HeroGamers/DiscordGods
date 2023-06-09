import discord
from discord import app_commands
from discord.ext import commands
import database
from Util.botutils import botutils


@app_commands.guild_only()
class Info(app_commands.Group, name="info"):
    def __init__(self, bot: discord.ext.commands.Bot):
        """Get information about different religions, as well as Leaderboards, locally or globally."""
        super().__init__()
        self.bot = bot

    # ------------ INFORMATION ------------ #

    @app_commands.command(name="godinfo")
    async def _info(self, interaction: discord.Interaction, name: str = None, show: bool = False):
        """Gets information about a God."""
        if name:
            god = database.getGodName(name, interaction.guild.id)
        else:
            believer = database.getBeliever(interaction.user.id, interaction.guild.id)
            if believer:
                god = database.getGod(believer.God)
            else:
                await interaction.response.send_message("Please give a God name!", ephemeral=True)
                return

        if not god:
            await interaction.response.send_message("That God doesn't exist!", ephemeral=True)
            return

        embedcolor = discord.Color.green()
        if god.Type:
            if god.Type.upper() == "YAOI":
                embedcolor = discord.Color.from_rgb(204, 235, 245)
            if god.Type.upper() == "TRAPS":
                embedcolor = discord.Color.from_rgb(248, 184, 248)
            for godtype in botutils.GodTypes:
                if godtype.name == god.Type:
                    embedcolor = godtype.getColor()

        title = god.Name + " - " + botutils.getGodString(god) + " of " + god.Type.capitalize()
        if god.Description:
            embed = discord.Embed(title=title, color=embedcolor,
                                  description=god.Description)
        else:
            embed = discord.Embed(title=title, color=embedcolor)
        embed.add_field(name="Creation Date",
                        value="%s" % god.CreationDate.strftime(
                            "%Y-%m-%d %H:%M:%S"), inline=True)
        believers = database.getBelieversByID(god.ID)
        if not believers:
            believers = []
        embed.add_field(name="Believers", value="%s" % len(believers), inline=True)
        embed.add_field(name="Power", value=round(god.Power, 1), inline=True)
        if god.Gender:
            embed.add_field(name="Gender:", value=god.Gender.capitalize(), inline=True)
        embed.add_field(name="Mood:", value=botutils.getGodMood(god.Mood), inline=True)
        embed.add_field(name="Invite Only:", value=god.InviteOnly, inline=True)
        if god.Priest:
            priest = await botutils.getUser(self.bot, interaction.guild, str(database.getBelieverByID(god.Priest).UserID))
            if priest:
                embed.set_footer(text="Priest: %s" % priest.name+"#"+priest.discriminator, icon_url=priest.avatar_url)
        else:
            embed.set_footer(text="This God has no priest yet!",
                             icon_url=self.bot.user.avatar)
        await interaction.response.send_message(embed=embed, ephemeral=show)

    @app_commands.command(name="gods")
    async def _list(self, interaction: discord.Interaction, show: bool = True):
        """Lists the top Gods on the server."""
        gods = database.getGods(interaction.guild.id)
        if not gods:
            await interaction.response.send_message("There are no Gods in " + interaction.guild.name + ", yet...", ephemeral=True)
            return

        gods = list(gods)

        i = 1
        godlist = ""

        for god in gods:
            if i > 15:
                break

            believers = database.getBelieversByID(god.ID)
            if not believers:
                believers = 0
            else:
                believers = len(database.getBelieversByID(god.ID))
            godtext = str("[" + str(i) + "]  > #" + god.Name + "\n"
                          "         " + botutils.getGodString(god) + " of " + god.Type.capitalize() + "\n"
                          "         Power: " + str(round(god.Power, 2)) + "\n"
                          "         Believers: " + str(believers) + "\n")
            godlist = godlist+godtext

            i += 1

        await interaction.response.send_message("**The Gods of " + interaction.guild.name + "**\n\n"
                       "```pl\n" + godlist + "```", ephemeral=show)

    @app_commands.command(name="globalgods")
    async def _globallist(self, interaction: discord.Interaction, show: bool = True):
        """Lists the top Gods globally."""
        gods = database.getGodsGlobal()
        if not gods:
            await interaction.response.send_message("There are no Gods, yet...", ephemeral=True)
            return

        gods = list(gods)

        i = 1
        godlist = ""

        for god in gods:
            if i > 10:
                break

            believers = database.getBelieversByID(god.ID)
            if not believers:
                believers = 0
            else:
                believers = len(database.getBelieversByID(god.ID))

            guild_name = "NaN"

            guild = self.bot.get_guild(int(god.Guild))
            if guild:
                guild_name = guild.name

            godtext = str("[" + str(i) + "]  > #" + god.Name + "\n"
                          "         " + botutils.getGodString(god) + " of " + god.Type.capitalize() + "\n"
                          "         Power: " + str(round(god.Power, 2)) + "\n"
                          "         Believers: " + str(believers) + "\n"
                          "         Server: " + guild_name + "\n")
            godlist = godlist + godtext

            i += 1

        await interaction.response.send_message("**The Global Gods Leaderboard**\n\n"
                       "```pl\n" + godlist + "```", ephemeral=show)

    @app_commands.command(name="marriages")
    async def _marriages(self, interaction: discord.Interaction, show: bool = True):
        """Lists the most loving married couples on the server."""
        marriages = database.getMarriages(interaction.guild.id)
        if not marriages:
            await interaction.response.send_message("There are no Marriages in " + interaction.guild.name + ", yet...", ephemeral=True)
            return

        marriages = list(marriages)

        i = 1
        marriagelist = ""

        for marriage in marriages:
            if i > 15:
                break

            believer1 = await botutils.getUser(self.bot, interaction.guild, database.getBelieverByID(marriage.Believer1).UserID)

            believer2 = await botutils.getUser(self.bot, interaction.guild, database.getBelieverByID(marriage.Believer2).UserID)

            god = database.getGod(marriage.God)

            marrytext = str("[" + str(i) + "]  > #" + believer1.name + " & " + believer2.name + "\n"
                            "         Loved: " + marriage.LoveDate.strftime("%Y-%m-%d %H:%M:%S") + "\n"
                            "         " + botutils.getGodString(god) + ": " + god.Name + "\n")
            marriagelist = marriagelist + marrytext

            i += 1

        await interaction.response.send_message("**The Married Couples of " + interaction.guild.name + "**\n\n"
                       "```pl\n" + marriagelist + "```", ephemeral=show)

    @app_commands.command(name="globalmarriages")
    async def _globalmarriages(self, interaction: discord.Interaction, show: bool = True):
        """Lists the most loving married couples globally."""
        marriages = database.getMarriagesGlobal()
        if not marriages:
            await interaction.response.send_message("There are no Marriages, yet...", ephemeral=True)
            return

        marriages = list(marriages)

        i = 1
        marriagelist = ""

        for marriage in marriages:
            if i > 10:
                break

            believer1 = await botutils.getUser(self.bot, interaction.guild, database.getBelieverByID(marriage.Believer1).UserID)

            believer2 = await botutils.getUser(self.bot, interaction.guild, database.getBelieverByID(marriage.Believer2).UserID)

            god = database.getGod(marriage.God)
            guild_name = "NaN"

            guild = self.bot.get_guild(int(god.Guild))
            if guild:
                guild_name = guild.name

            marrytext = str("[" + str(i) + "]  > #" + believer1.name + " & " + believer2.name + "\n"
                            "         Loved: " + marriage.LoveDate.strftime("%Y-%m-%d %H:%M:%S") + "\n"
                            "         " + botutils.getGodString(god) + ": " + god.Name + "\n"
                            "         Server: " + guild_name + "\n")
            marriagelist = marriagelist + marrytext

            i += 1

        await interaction.response.send_message("**The Global Married Couples Leaderboard**\n\n"
                       "```pl\n" + marriagelist + "```", ephemeral=show)
