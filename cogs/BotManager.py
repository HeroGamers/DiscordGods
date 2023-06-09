from typing import Literal
import discord
from discord import app_commands
from discord.ext import commands
import database
from Util import logger
import Util.botutils as utilchecks


class BotManager(app_commands.Group, name="bot"):
    def __init__(self, bot: discord.ext.commands.Bot):
        """Where is the source code? How can I invite the bot? All these questions have their answers right here."""
        super().__init__()
        self.bot = bot

    @app_commands.command(name="howto")
    async def _howto(self, interaction: discord.Interaction, category: Literal["management", "miscellaneous"]):
        """Get help on how to use Gods."""
        if not category:
            await interaction.response.send_message("```\n"
                           "So... You want to start a new religion. Or, maybe you want to join an already existing "
                           "religion? Wait... oh, you are already experienced in the ways of Gods? Well, there are "
                           "categories to further expand your knowledge around this mess of commands!\n"
                           "\n"
                           "  <> = required argument. [] = optional argument.\n"
                           "\n"
                           "> Creating a new religion:\n"
                           "    /god create <godName> [gender]   "
                                             "Create a new religion. Gender is optional.\n"
                           "> Joining an already created religion:\n"
                           "    /believer join <godName>              "
                                             "Joins a religion.\n"
                           "> Praying to your God:\n"
                           "    /believer pray                        "
                                             "Prays to a God, raising it's Power and Mood, and gaining Prayer Power.\n"
                           "\n"
                           "For more specialized help, use '/bot howto [category]'.\n"
                           "Categories:\n"
                           "  Management                          "
                           "Gets help about managing a God. Directed towards Priests.\n"
                           "  Misc                                "
                           "Miscellaneous things like marriage and hugs.\n"
                           "```", ephemeral=True)
        else:
            if category.lower() == "management":
                await interaction.response.send_message("```\n"
                               "Phew, the management of religions. These commands are for Priests only.\n"
                               "\n"
                               "  <> = required argument. [] = optional argument.\n"
                               "\n"
                               "> Set your religion to invite-only:\n"
                               "    /god lock                      "
                                                 "Set your religion as open or invite only.\n"
                               "> Change the description of your religion:\n"
                               "    /god description <desc>          "
                                                 "Sets a description.\n"
                               "> Invite someone to your religion:\n"
                               "    /god invite <mention or ID>      "
                                                 "Invites said user to your religion.\n"
                               "> Set the gender of your God:\n"
                               "    /god setgender <gender>          "
                                                 "Changes the gender of your God. Examples include female and "
                                                 "sexless.\n"
                               "> Set the type of your God:\n"
                               "    /god settype <type>              "
                                                 "Example types include Love, War and Thunder.\n"
                               "```", ephemeral=True)
            elif (category.lower() == "misc") or (category.lower() == "miscellaneous"):
                await interaction.response.send_message("```\n"
                               "So, you wanna get married, huh?\n"
                               "\n"
                               "  <> = required argument. [] = optional argument.\n"
                               "\n"
                               "> Marrying someone:\n"
                               "    /believer marry <user>       "
                                                 "Proposes to marry someone. The person you marry must believe in the "
                                                 "same religion as you.\n"
                               "> Loving/kissing your lover:\n"
                               "    /misc love                        "
                                                 "Kisses your special someone, bringing you to the top of the"
                                                 "marriage list. This costs no Prayer Power.\n"
                               "> Hug someone:\n"
                               "    /misc hug <user>         "
                                                 "Hugs someone - Costs 0.5 Prayer Power.\n"
                               "```", ephemeral=True)
            else:
                await interaction.response.send_message("Category not found!", ephemeral=True)

    @app_commands.command(name="sourcecode")
    async def _source(self, interaction: discord.Interaction):
        """View and/or help with the source code of Gods."""
        await interaction.response.send_message("The source code for Gods can be found here: https://github.com/HeroGamers/DiscordGods", ephemeral=True)

    @app_commands.command(name="support")
    async def _support(self, interaction: discord.Interaction):
        """Get help and support regarding the bot."""
        await interaction.response.send_message("The server where the Gods roam, Treeland: https://discord.gg/PvFPEfd", ephemeral=True)

    @app_commands.command(name="botinvite")
    async def _botinvite(self, interaction: discord.Interaction):
        """How to invite the bot."""
        await interaction.response.send_message(
            "Invite me to your server with this link: "
            "<https://discordapp.com/oauth2/authorize?scope=bot&client_id=180405652605239296>", ephemeral=True)

    @app_commands.command(name="botinfo")
    async def _botinfo(self, interaction: discord.Interaction):
        """Retrives information about the bot."""
        embed = discord.Embed(title="Bot Information", color=discord.Color.green(),
                              description="")
        embed.add_field(name="Creation Date",
                        value="%s" % discord.utils.snowflake_time(self.bot.user.id).strftime(
                            "%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Guilds", value="%s" % len(self.bot.guilds), inline=True)
        embed.add_field(name="Gods", value="%s" % str(database.getGodsGlobalCount()), inline=True)
        embed.add_field(name="Believers", value="%s" % str(database.getBelieversGlobalCount()), inline=True)
        embed.add_field(name="Privacy Policy", value="For the Privacy Policy, please [click here](https://gist.github.com/HeroGamers/a92b824d899981c4c6c287978a54548c)!", inline=True)
        embed.set_footer(text="%s" % interaction.user.name,
                         icon_url=interaction.user.avatar_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="loadcog")
    @app_commands.check(utilchecks.isOwner)
    async def _loadcog(self, interaction: discord.Interaction, cog: str):
        """Loads a cog."""
        bot = self.bot
        try:
            await bot.load_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"Successfully loaded the {cog} extension", ephemeral=True)
            await logger.log("Moderator `%s` loaded the extension %s" % (interaction.user.name, cog), bot, "INFO")
        except Exception as e:
            await interaction.response.send_message(f"Failed to load the extension {cog}", ephemeral=True)
            await logger.log(f"Failed to load the extension {cog} - {e}", bot, "ERROR")

    @app_commands.command(name="cogs")
    @app_commands.check(utilchecks.isOwner)
    async def _listcogs(self, interaction: discord.Interaction):
        """Lists all the cogs."""
        embed = discord.Embed(title="Cogs", color=discord.Color.green(),
                              description="`AdminManager, BelieverManager, BotLists, BotManager, GodManager, Info, "
                                          "Misc, Tasks`")
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="unloadcog")
    @app_commands.check(utilchecks.isOwner)
    async def _unloadcog(self, interaction: discord.Interaction, cog: str):
        """Unloads a cog."""
        bot = self.bot
        try:
            await bot.unload_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"Successfully unloaded the {cog} extension", ephemeral=True)
            await logger.log("Moderator `%s` unloaded the extension %s" % (interaction.user.name, cog), bot, "INFO")
        except Exception as e:
            await interaction.response.send_message(f"Failed to unload the extension {cog}", ephemeral=True)
            await logger.log(f"Failed to unload the extension {cog} - {e}", bot, "ERROR")
