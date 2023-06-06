import discord.ext.commands
from discord import app_commands
import database
from Util.botutils import botutils


class AdminManager(app_commands.Group, name="administrator"):
    def __init__(self, bot: discord.ext.commands.Bot):
        """For Server Administrators to manage the Gods and how DiscordGods work on the server."""
        super().__init__()
        self.bot = bot

    # ------------ SERVER MANAGEMENT ------------ #

    # ------------ GOD MANAGEMENT ------------ #

    @app_commands.command(name="forcedescription")
    @app_commands.checks.has_permissions(administrator=True)
    async def _forcedescription(self, interaction: discord.Interaction, name: str, description: str):
        """Forces a description for a religion."""
        if not name or not description:
            await interaction.response.send_message("Include both a name and a description!", ephemeral=True)
            return

        god = database.getGodName(name, interaction.guild.id)

        if god:
            if len(description) > 100:
                await interaction.response.send_message("Keep the description under 100 chars, please.", ephemeral=True)
                return

            database.setDesc(god.ID, description)
            await interaction.response.send_message("Description set successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("No God found by that name!", ephemeral=True)

    @app_commands.command(name="forcesettype")
    @app_commands.checks.has_permissions(administrator=True)
    async def _forcesettype(self, interaction: discord.Interaction, name: str, godtype: botutils.GodTypes):
        """Set the type of a God to something else."""
        if not name or not godtype:
            await interaction.response.send_message("Include both a name and a type!", ephemeral=True)
            return

        god = database.getGodName(name, interaction.guild.id)
        if god:
            if godtype:
                database.setType(god.ID, godtype.name)
                await interaction.response.send_message("Set your God's type successfully!", ephemeral=True)
            else:
                await interaction.response.send_message("Please choose between these types: `" + ','.join([godtype.name for godtype in botutils.GodTypes]) + "`!", ephemeral=True)

    @app_commands.command(name="forcesetgender")
    @app_commands.checks.has_permissions(administrator=True)
    async def _forcesetgender(self, interaction: discord.Interaction, name: str, gender: str):
        """Set the gender of a God to something else."""
        if not name or not gender:
            await interaction.response.send_message("Include both a name and a gender!", ephemeral=True)
            return

        god = database.getGodName(name, interaction.guild.id)
        if god:
            if len(gender) > 19:
                await interaction.response.send_message("Please choose a gender that's not longer than 19 characters!", ephemeral=True)
                return

            database.setGender(god.ID, gender)
            await interaction.response.send_message("Gender successfully set to: " + gender + "!", ephemeral=True)

    @app_commands.command(name="forcesetpriest")
    @app_commands.checks.has_permissions(administrator=True)
    async def _forcesetpriest(self, interaction: discord.Interaction, name: str, member: discord.Member):
        """Set the priest of a God."""
        if not member or not name:
            await interaction.response.send_message("Include both a name and a user.", ephemeral=True)
            return

        god = database.getGodName(name, interaction.guild.id)
        if god:
            if not member:
                await interaction.response.send_message("Could not fetch user!", ephemeral=True)
                return

            believer = database.getBeliever(member.id, interaction.guild.id)

            if believer:
                if believer.God.ID != god.ID:
                    database.setGod(believer.ID, god.ID)
            else:
                believer = database.newBeliever(member.id, god.ID)

            database.setPriest(god.ID, believer.ID)

            await interaction.response.send_message("Priest successfully set!", ephemeral=True)

    @app_commands.command(name="forcedeletegod")
    @app_commands.checks.has_permissions(administrator=True)
    async def _forcedeletegod(self, interaction: discord.Interaction, name: str):
        """Removes a religion from the server."""
        if not name:
            await interaction.response.send_message("No name given!", ephemeral=True)
        god = database.getGodName(name, interaction.guild.id)
        if god:
            if botutils.disbandGod(god.ID):
                await interaction.response.send_message("God disbanded successfully!", ephemeral=True)
            else:
                await interaction.response.send_message("An error occurred doing that!", ephemeral=True)
        else:
            await interaction.response.send_message("A god with that name doesn't exist!")
