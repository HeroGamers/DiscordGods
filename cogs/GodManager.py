import random

import discord
from discord import app_commands
from discord.ext import commands
import database
from Util import logger
from Util.botutils import botutils
from Util import botutils as utilchecks


@app_commands.guild_only()
class GodManager(app_commands.Group, name="god"):
    def __init__(self, bot: discord.ext.commands.Bot):
        """Manage the religions, create new religions, and set their types as a priest."""
        super().__init__()
        self.bot = bot

    # ------------ GOD MANAGEMENT ------------ #

    @app_commands.command(name="create")
    @app_commands.check(utilchecks.isNotBeliever)
    async def _create(self, interaction: discord.Interaction, name: str, gender: str = None):
        """Creates a new God."""
        user = interaction.user

        if database.getBeliever(user.id, interaction.guild.id):
            await interaction.response.send_message("You are already in a God, please leave it to create a new one!", ephemeral=True)
            return

        if not name:
            await interaction.response.send_message("Please give your God a name!", ephemeral=True)
            return

        if database.getGodName(name, interaction.guild.id):
            await interaction.response.send_message("A God with that name already exists!", ephemeral=True)
            return

        if len(name) > 16:
            await interaction.response.send_message("Please choose a name that's not longer than 16 characters!", ephemeral=True)
            return

        if gender:
            if len(gender) > 19:
                await interaction.response.send_message("Please choose a gender that's not longer than 19 characters!", ephemeral=True)
                return

            god = database.newGod(interaction.guild.id, name, random.choice(list(botutils.GodTypes)).name, gender)
        else:
            god = database.newGod(interaction.guild.id, name, random.choice(list(botutils.GodTypes)).name)
        if god.ID:
            await interaction.response.send_message("God created!", ephemeral=True)
            believer = database.newBeliever(user.id, god)
            if believer.ID:
                logger.logDebug("Believer created!")
        else:
            await interaction.response.send_message("Boohoo, God creation failed...", ephemeral=True)

    @app_commands.command(name="lock")
    @app_commands.check(utilchecks.isPriest)
    async def _access(self, interaction: discord.Interaction):
        """Set your religion as open or invite only."""
        god = database.getBeliever(interaction.user.id, interaction.guild.id).God

        if god:
            if database.toggleAccess(god.ID):
                await interaction.response.send_message("God is now Invite Only!", ephemeral=True)
            else:
                await interaction.response.send_message("God is now Open!", ephemeral=True)

    # @app_commands.command(name="ally", aliases=["friend"])
    # @app_commands.check(utilchecks.isPriest)
    # async def _ally(self, interaction: discord.Interaction):
    #     """Toggles alliance with another religion - Not done"""
    #     logger.logDebug("yes")
    #
    # @app_commands.command(name="war", aliases=["enemy"])
    # @app_commands.check(utilchecks.isPriest)
    # async def _war(self, interaction: discord.Interaction):
    #     """Toggles war with another religion - Not done"""
    #     logger.logDebug("yes")

    @app_commands.command(name="description")
    @app_commands.check(utilchecks.isPriest)
    async def _description(self, interaction: discord.Interaction, description: str):
        """Sets a description for your religion."""
        god = database.getBeliever(interaction.user.id, interaction.guild.id).God

        if god:
            if len(description) > 100:
                await interaction.response.send_message("Keep your description under 100 chars, please.", ephemeral=True)
                return

            database.setDesc(god.ID, description)
            await interaction.response.send_message("Description set successfully!", ephemeral=True)

    @app_commands.command(name="invite")
    @app_commands.check(utilchecks.isPriest)
    async def _invite(self, interaction: discord.Interaction, user: discord.Member):
        """Invite someone to your religion."""
        god = database.getBeliever(interaction.user.id, interaction.guild.id).God
        if god:
            if not user:
                await interaction.response.send_message("User not found!", ephemeral=True)
                return

            if user.bot:
                await interaction.response.send_message("Sorry, but I don't think the bot is going to respond to your invitation...", ephemeral=True)
                return

            if not interaction.guild.get_member(user.id):
                if not (await interaction.guild.fetch_member(user.id)):
                    await interaction.response.send_message("The user is not in this server!", ephemeral=True)
                    return

            believer = database.getBeliever(user.id, interaction.guild.id)
            if believer:
                if believer.God.ID == god.ID:
                    await interaction.response.send_message(user.name + " is already in your religion!", ephemeral=True)
                    return

            invite = database.getInvite(user.id, god.ID)
            if invite:
                await interaction.response.send_message("You already have an active invite for this user to join your God! Tell them to join!", ephemeral=True)
                return

            if database.newInvite(god.ID, user.id):
                await interaction.response.send_message("An invite to your religion has been sent to the user!\n"
                               "*Invites will become invalid 24 hours after being issued.*", ephemeral=True)
            else:
                await interaction.response.send_message("Creating the invite failed!", ephemeral=True)

    @app_commands.command(name="settype")
    @app_commands.check(utilchecks.isPriest)
    async def _settype(self, interaction: discord.Interaction, godtype: botutils.GodTypes):
        """Set the type of your God to something else."""
        god = database.getBeliever(interaction.user.id, interaction.guild.id).God
        if god:
            if godtype:
                database.setType(god.ID, godtype.name)
                await interaction.response.send_message("Set your God's type successfully!", ephemeral=True)
            else:
                await interaction.response.send_message("Please choose between these types: `" + ','.join([godtype.name for godtype in botutils.GodTypes]) + "`!", ephemeral=True)

    @app_commands.command(name="setgender")
    @app_commands.check(utilchecks.isPriest)
    async def _setgender(self, interaction: discord.Interaction, gender: str):
        """Set the gender of your God to something else."""
        god = database.getBeliever(interaction.user.id, interaction.guild.id).God
        if god:
            if len(gender) > 19:
                await interaction.response.send_message("Please choose a gender that's not longer than 19 characters!", ephemeral=True)
                return

            database.setGender(god.ID, gender)
            await interaction.response.send_message("Gender successfully set to: " + gender + "!", ephemeral=True)
